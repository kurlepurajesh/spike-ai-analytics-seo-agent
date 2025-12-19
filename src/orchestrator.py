from typing import Dict, Any, Optional
import os
from openai import OpenAI, APIError
import json
import time
import logging
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        # Initialize LiteLLM client with proper HTTP client (no SSL for HTTP-only proxy)
        self.client = OpenAI(
            api_key=os.environ.get("LITELLM_API_KEY", "sk-placeholder"),
            base_url="http://3.110.18.218",
            http_client=httpx.Client(verify=False),
            timeout=120.0
        )

    def route_query(self, query: str, property_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Determines the intent of the query and routes it to the appropriate agent.
        """
        logger.info(f"Routing query: {query[:100]}...")
        
        # Detect if user wants JSON output
        wants_json = self._detect_json_output(query)
        
        # LLM-based intent detection
        intent = self._detect_intent(query, property_id)
        logger.info(f"Detected intent: {intent}")
        
        result = None
        if intent == "analytics":
            if not property_id:
                return {"error": "Property ID is required for analytics queries."}
            result = self._call_analytics_agent(query, property_id)
        elif intent == "seo":
            result = self._call_seo_agent(query)
        elif intent == "fusion":
            if not property_id:
                return {"error": "Property ID is required for fusion queries involving analytics data."}
            result = self._call_fusion_agent(query, property_id)
        else:
            return {"error": "Unable to determine query intent."}
        
        # Format output as JSON if requested
        if wants_json and result and "data" in result:
            return {"data": result["data"]}
        
        return result

    def _detect_json_output(self, query: str) -> bool:
        """Detects if user wants JSON output."""
        query_lower = query.lower()
        return any(phrase in query_lower for phrase in [
            "json", "json format", "in json", "as json", "return json"
        ])

    def _detect_intent(self, query: str, property_id: Optional[str]) -> str:
        """
        Uses LLM to detect the intent of the query.
        """
        prompt = f"""You are an intent classifier for an analytics and SEO system.

Classify the following query into ONE of these categories:
- "analytics": Queries about web traffic, users, sessions, page views, traffic sources, GA4 data
- "seo": Queries about URLs, title tags, meta descriptions, indexability, HTTPS, technical SEO
- "fusion": Queries that require BOTH analytics AND SEO data (e.g., "top pages by views with their title tags")

Query: "{query}"
Property ID provided: {property_id is not None}

Respond with ONLY one word: analytics, seo, or fusion"""
        
        try:
            response = self._call_llm_with_retry(prompt, model="gemini-2.5-flash")
            intent = response.strip().lower()
            
            if intent in ["analytics", "seo", "fusion"]:
                return intent
            
            # Fallback logic
            query_lower = query.lower()
            if any(kw in query_lower for kw in ["page views", "sessions", "users", "traffic", "ga4"]):
                return "analytics"
            elif any(kw in query_lower for kw in ["title", "url", "https", "indexability", "meta"]):
                return "seo"
            else:
                return "analytics" if property_id else "seo"
        except Exception as e:
            logger.error(f"Intent detection failed: {e}")
            # Fallback to keyword-based
            query_lower = query.lower()
            if any(kw in query_lower for kw in ["page views", "sessions", "users"]):
                return "analytics"
            return "seo"

    def _call_llm_with_retry(self, prompt: str, model: str = "gemini-2.5-flash", max_retries: int = 5) -> str:
        """
        Calls LLM with exponential backoff for rate limiting.
        """
        base_delay = 1
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    timeout=120
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

    def _call_analytics_agent(self, query: str, property_id: str) -> Dict[str, Any]:
        from src.agents.analytics_agent import AnalyticsAgent
        agent = AnalyticsAgent()
        return agent.process_query(query, property_id)

    def _call_seo_agent(self, query: str) -> Dict[str, Any]:
        from src.agents.seo_agent import SeoAgent
        agent = SeoAgent()
        return agent.process_query(query)

    def _call_fusion_agent(self, query: str, property_id: Optional[str]) -> Dict[str, Any]:
        """
        Handles complex queries requiring both Analytics and SEO data.
        """
        if not property_id:
            return {"error": "Property ID is required for fusion queries."}

        # 1. Decompose Query (LLM)
        plan = self._decompose_query(query)
        
        # 2. Execute Analytics Sub-query
        analytics_result = self._call_analytics_agent(plan['analytics_query'], property_id)
        
        # 3. Execute SEO Sub-query
        # We might need to pass context from analytics result to SEO query, 
        # but for now we'll assume independent or simple dependency
        seo_result = self._call_seo_agent(plan['seo_query'])
        
        # 4. Fuse Data
        fused_data = self._fuse_data(analytics_result.get('data', {}), seo_result.get('data', []))
        
        # 5. Generate Final Response
        final_answer = self._generate_fusion_response(query, fused_data)
        
        return {
            "answer": final_answer,
            "data": fused_data
        }

    def _decompose_query(self, query: str) -> Dict[str, str]:
        """
        Decomposes a fusion query into analytics and SEO parts.
        """
        prompt = f"""
        You are a query planner.
        Decompose the following complex query into two sub-queries:
        1. An Analytics query (for GA4)
        2. An SEO query (for Screaming Frog data)
        
        Query: "{query}"
        
        Respond with a JSON object:
        {{
            "analytics_query": "...",
            "seo_query": "..."
        }}
        """
        
        response = self._call_llm_with_retry(prompt)
        
        content = response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        return json.loads(content.strip())

    def _fuse_data(self, analytics_data: Dict[str, Any], seo_data: list) -> Dict[str, Any]:
        """
        Intelligently combines Analytics and SEO data by joining on URL/page path.
        """
        # Extract analytics rows
        analytics_rows = analytics_data.get("rows", [])
        
        # Build a map of page paths from SEO data
        seo_map = {}
        for seo_row in seo_data:
            address = seo_row.get("Address", "")
            if address:
                # Normalize URL to path for matching
                from urllib.parse import urlparse
                path = urlparse(address).path if address.startswith("http") else address
                seo_map[path] = seo_row
        
        # Join analytics and SEO data
        fused_results = []
        for analytics_row in analytics_rows:
            page_path = analytics_row.get("pagePath", analytics_row.get("pagePathPlusQueryString", ""))
            
            fused_row = {
                "analytics": analytics_row,
                "seo": seo_map.get(page_path, {})
            }
            fused_results.append(fused_row)
        
        return {
            "fused_data": fused_results,
            "analytics_count": len(analytics_rows),
            "seo_count": len(seo_data),
            "matched_count": sum(1 for r in fused_results if r["seo"])
        }

    def _generate_fusion_response(self, query: str, fused_data: Dict[str, Any]) -> str:
        """
        Generates a natural language response from fused data.
        """
        # Limit data size for LLM context
        limited_data = fused_data.copy()
        if "fused_data" in limited_data:
            limited_data["fused_data"] = limited_data["fused_data"][:10]
        
        prompt = f"""
        You are a smart assistant.
        User Query: "{query}"
        Fused Data: {json.dumps(limited_data, indent=2)}
        
        Provide a comprehensive answer combining insights from both Analytics and SEO data.
        Correlate the data points (e.g., "Pages with high traffic but poor SEO metadata").
        Explain the relationship between the metrics and provide actionable insights.
        """
        
        response = self._call_llm_with_retry(prompt)
        
        return response
