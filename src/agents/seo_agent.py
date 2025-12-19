from typing import Dict, Any
import pandas as pd
import os
import json
import time
import logging
import httpx
from openai import OpenAI, APIError
import io
import requests
import warnings

# Suppress pandas SettingWithCopyWarning
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeoAgent:
    def __init__(self):
        # Initialize LiteLLM client with proper HTTP client
        self.llm_client = OpenAI(
            api_key=os.environ.get("LITELLM_API_KEY", "sk-placeholder"),
            base_url="http://3.110.18.218",
            http_client=httpx.Client(verify=False),
            timeout=60.0
        )
        
        # Load SEO data
        # Using the provided Google Sheet ID
        self.sheet_id = "1zzf4ax_H2WiTBVrJigGjF2Q3Yz-qy2qMCbAMKvl6VEE"
        self.gid = "1438203274"
        self.csv_url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/export?format=csv&gid={self.gid}"

    def _load_data(self) -> pd.DataFrame:
        try:
            # Fetch live data on every request
            logger.info(f"Loading SEO data from Google Sheets...")
            response = requests.get(self.csv_url, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
                # Fill NaN values with 0 for numeric columns, empty string for others
                for col in df.columns:
                    if df[col].dtype in ['float64', 'int64']:
                        df[col] = df[col].fillna(0)
                    else:
                        df[col] = df[col].fillna('')
                logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
                logger.info(f"Columns: {df.columns.tolist()}")
                return df
            else:
                logger.error(f"Failed to load SEO data: {response.status_code}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading SEO data: {e}")
            return pd.DataFrame()

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Processes a natural language query for SEO data.
        """
        # Load data FRESH for every query
        df = self._load_data()
        
        if df.empty:
            return {"error": "SEO data not available."}

        retries = 3
        last_error = None
        
        for attempt in range(retries):
            try:
                # 1. Convert NL to Pandas Filter (LLM)
                filter_code = self._generate_pandas_filter(query, df, error=last_error)
                
                # 2. Execute Filter
                result_df = self._execute_filter(filter_code, df)
                
                # 3. Generate NL Response (LLM)
                answer = self._generate_nl_response(query, result_df)
                
                # Replace NaN with None for JSON serialization
                result_dict = result_df.where(pd.notna(result_df), None).to_dict(orient="records")
                
                return {
                    "answer": answer,
                    "data": result_dict,
                    "thought_process": {
                        "steps": attempt + 1,
                        "final_code": filter_code
                    }
                }
            except Exception as e:
                last_error = str(e)
                print(f"Attempt {attempt + 1} failed: {last_error}")
                continue

        return {"error": f"Failed after {retries} attempts. Last error: {last_error}"}

    def _generate_pandas_filter(self, query: str, df: pd.DataFrame, error: str = None) -> str:
        """
        Uses LLM to generate a Pandas filter expression.
        """
        columns = df.columns.tolist()
        columns_str = ", ".join([f"'{col}'" for col in columns])
        
        # Get sample data to help LLM understand the structure
        sample_data = df.head(2).to_dict(orient='records')
        
        prompt = f"""
        You are a Pandas expert.
        User Query: "{query}"
        
        Available DataFrame Columns: {columns_str}
        
        Sample Data (first 2 rows):
        {json.dumps(sample_data, indent=2)}
        
        IMPORTANT:
        - Use EXACT column names from the list above (with proper quotes/spacing)
        - The DataFrame is called `df`
        - Return a DataFrame with relevant columns, not just a Series
        - Use .str methods for string operations
        - Use proper pandas filtering syntax
        - DO NOT use .to_json(), .to_dict(), or any serialization methods
        - Just return the DataFrame filter expression
        
        Write a Python expression that filters/processes the DataFrame to answer the query.
        Do NOT import pandas. Assume `df` exists.
        """
        
        if error:
            prompt += f"\n\nPREVIOUS ATTEMPT FAILED WITH ERROR: {error}\nFIX THE CODE. Check column names carefully!"
            
        prompt += """
        
        Examples of correct syntax:
        - df[df['Address'].str.contains('https')][['Address']]
        - df[df['Title 1'].str.len() > 60][['Address', 'Title 1']]
        - df.groupby('Indexability')['Address'].count()
        
        Respond ONLY with the Python expression. NO explanations.
        """
        
        response = self._call_llm_with_retry(prompt)
        
        content = response
        # Clean up code blocks
        if "```python" in content:
            content = content.split("```python")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        code = content.strip()
        logger.info(f"Generated pandas filter: {code}")
        return code

    def _call_llm_with_retry(self, prompt: str, model: str = "gemini-2.5-flash", max_retries: int = 5) -> str:
        """
        Calls LLM with exponential backoff for rate limiting.
        """
        base_delay = 1
        for attempt in range(max_retries):
            try:
                response = self.llm_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    timeout=30
                )
                return response.choices[0].message.content
            except APIError as e:
                if e.status_code == 429:
                    wait_time = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limited (429). Retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API Error: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
        
        raise Exception("Failed to call LLM after max retries")

    def _execute_filter(self, code: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes the generated Pandas code safely.
        """
        local_vars = {"df": df, "pd": pd}
        try:
            result = eval(code, {"pd": pd}, local_vars)
            # Convert to DataFrame if needed
            if isinstance(result, pd.Series):
                result = result.to_frame()
            elif not isinstance(result, pd.DataFrame):
                # If result is not a DataFrame (e.g., string, int), return empty DataFrame
                logger.warning(f"Filter returned non-DataFrame type: {type(result)}")
                return pd.DataFrame()
            
            # Fill any remaining NaN values
            for col in result.columns:
                if result[col].dtype in ['float64', 'int64']:
                    result[col] = result[col].fillna(0)
                else:
                    result[col] = result[col].fillna('')
            
            return result
        except Exception as e:
            raise Exception(f"Failed to execute filter: {e}")

    def _generate_nl_response(self, query: str, result_df: pd.DataFrame) -> str:
        """
        Uses LLM to generate a natural language response from the result DataFrame.
        """
        # Handle empty results
        if result_df.empty:
            return "No data matched the query criteria."
        
        # Limit the data sent to LLM to avoid token limits
        data_summary = result_df.head(10).to_dict(orient="records")
        row_count = len(result_df)
        
        prompt = f"""
        You are an SEO expert.
        User Query: "{query}"
        Result Data (First 10 rows of {row_count} total): {json.dumps(data_summary, indent=2)}
        
        Provide a clear, concise natural language answer to the user's query based on the data.
        If there are more results than shown, mention the total count.
        Highlight important SEO issues or insights.
        """
        
        response = self._call_llm_with_retry(prompt)
        
        return response
