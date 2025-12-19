import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="Spike AI Hackathon - Multi-Agent Analytics & SEO System",
    version="1.0.0",
    description="Production-ready AI backend for GA4 Analytics and SEO Audits"
)

# Input Model per API Contract
class QueryRequest(BaseModel):
    query: str
    propertyId: Optional[str] = None  # Optional for SEO-only queries

@app.post("/query")
def handle_query(request: QueryRequest):
    """
    Main entry point for the Orchestrator.
    Routes queries to appropriate agents based on intent.
    """
    logger.info(f"Received query: {request.query[:100]}...")
    
    try:
        # Check for GA4 Credentials
        if not os.path.exists("credentials.json"):
            logger.warning("credentials.json not found. GA4 queries will fail.")
        
        # Route through orchestrator
        from src.orchestrator import Orchestrator
        orchestrator = Orchestrator()
        result = orchestrator.route_query(request.query, request.propertyId)
        
        logger.info(f"Query processed successfully")
        return result

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e),
                "query": request.query[:100]
            }
        )

@app.get("/health")
def health():
    """
    Health check endpoint.
    """
    checks = {
        "status": "ok",
        "credentials": os.path.exists("credentials.json"),
        "env_loaded": "LITELLM_API_KEY" in os.environ
    }
    return checks

@app.get("/")
def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Spike AI Hackathon - Multi-Agent System",
        "version": "1.0.0",
        "endpoints": {
            "query": "POST /query",
            "health": "GET /health"
        },
        "tiers": ["analytics", "seo", "fusion"]
    }
