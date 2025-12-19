#!/usr/bin/env python3
"""
Comprehensive test script for Spike AI Hackathon submission.
Tests Tier 1, Tier 2, and Tier 3 queries.
"""

import requests
import json
import sys
import time
from typing import Dict, Any

# Configuration
API_URL = "http://localhost:8080/query"
# Replace with your actual GA4 Property ID
PROPERTY_ID = "516812130"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test_query(query: str, property_id: str = None, tier: str = "", description: str = ""):
    """
    Test a single query against the API.
    """
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}[{tier}] {description}{RESET}")
    print(f"{YELLOW}Query: {query}{RESET}")
    
    payload = {"query": query}
    if property_id:
        payload["propertyId"] = property_id
    
    try:
        start_time = time.time()
        response = requests.post(API_URL, json=payload, timeout=60)
        elapsed_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"{GREEN}✓ SUCCESS{RESET}")
            print(f"\nResponse:")
            print(json.dumps(result, indent=2)[:1000])  # Limit output
            if len(json.dumps(result)) > 1000:
                print(f"... (truncated)")
            return True
        else:
            print(f"{RED}✗ FAILED{RESET}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"{RED}✗ EXCEPTION: {e}{RESET}")
        return False

def main():
    """
    Run all test queries.
    """
    print(f"{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}SPIKE AI HACKATHON - COMPREHENSIVE TEST SUITE{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    if PROPERTY_ID == "YOUR_GA4_PROPERTY_ID":
        print(f"{RED}ERROR: Please update PROPERTY_ID in test_queries.py{RESET}")
        sys.exit(1)
    
    # Check if server is running
    try:
        health = requests.get("http://localhost:8080/health", timeout=5)
        if health.status_code == 200:
            print(f"{GREEN}✓ Server is running{RESET}")
        else:
            print(f"{RED}✗ Server health check failed{RESET}")
            sys.exit(1)
    except Exception as e:
        print(f"{RED}✗ Server is not running: {e}{RESET}")
        print(f"{YELLOW}Please start the server with: bash deploy.sh{RESET}")
        sys.exit(1)
    
    results = {"passed": 0, "failed": 0}
    
    # ========================================================================
    # TIER 1: ANALYTICS AGENT (GA4)
    # ========================================================================
    
    tier1_queries = [
        {
            "query": "Give me a daily breakdown of page views, users, and sessions for the /pricing page over the last 14 days. Summarize any noticeable trends.",
            "description": "Daily Metrics Breakdown"
        },
        {
            "query": "What are the top 5 traffic sources driving users to the pricing page in the last 30 days?",
            "description": "Traffic Source Analysis"
        },
        {
            "query": "Calculate the average daily page views for the homepage over the last 30 days. Compare it to the previous 30-day period and explain whether traffic is increasing or decreasing.",
            "description": "Calculated Insight (LLM Reasoning)"
        },
        {
            "query": "How many active users in the last 7 days?",
            "description": "Simple Active Users Query"
        },
        {
            "query": "What is the total number of sessions in the last week?",
            "description": "Total Sessions Query"
        }
    ]
    
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}TIER 1: ANALYTICS AGENT (GA4){RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    for test in tier1_queries:
        success = test_query(
            query=test["query"],
            property_id=PROPERTY_ID,
            tier="TIER 1",
            description=test["description"]
        )
        results["passed" if success else "failed"] += 1
        time.sleep(1)  # Rate limiting
    
    # ========================================================================
    # TIER 2: SEO AGENT (SCREAMING FROG)
    # ========================================================================
    
    tier2_queries = [
        {
            "query": "Which URLs do not use HTTPS and have title tags longer than 60 characters?",
            "description": "Conditional Filtering"
        },
        {
            "query": "Group all pages by indexability status and provide a count for each group with a brief explanation.",
            "description": "Indexability Overview"
        },
        {
            "query": "Calculate the percentage of indexable pages on the site. Based on this number, assess whether the site's technical SEO health is good, average, or poor.",
            "description": "Calculated SEO Insight (LLM Reasoning)"
        },
        {
            "query": "Which URLs have title length > 60?",
            "description": "Simple Title Length Filter"
        },
        {
            "query": "Show me all pages with missing meta descriptions",
            "description": "Missing Meta Descriptions"
        }
    ]
    
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}TIER 2: SEO AGENT (SCREAMING FROG){RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    for test in tier2_queries:
        success = test_query(
            query=test["query"],
            property_id=None,  # No property ID for SEO-only queries
            tier="TIER 2",
            description=test["description"]
        )
        results["passed" if success else "failed"] += 1
        time.sleep(1)  # Rate limiting
    
    # ========================================================================
    # TIER 3: MULTI-AGENT SYSTEM (FUSION)
    # ========================================================================
    
    tier3_queries = [
        {
            "query": "What are the top 10 pages by page views in the last 14 days, and what are their corresponding title tags?",
            "description": "Analytics + SEO Fusion"
        },
        {
            "query": "Which pages are in the top 20% by views but have missing or duplicate meta descriptions? Explain the SEO risk.",
            "description": "High Traffic, High Risk Pages"
        },
        {
            "query": "Return the top 5 pages by views along with their title tags and indexability status in JSON format.",
            "description": "Cross-Agent JSON Output"
        }
    ]
    
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}TIER 3: MULTI-AGENT SYSTEM (FUSION){RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    for test in tier3_queries:
        success = test_query(
            query=test["query"],
            property_id=PROPERTY_ID,
            tier="TIER 3",
            description=test["description"]
        )
        results["passed" if success else "failed"] += 1
        time.sleep(1)  # Rate limiting
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    print(f"{GREEN}Passed: {results['passed']}{RESET}")
    print(f"{RED}Failed: {results['failed']}{RESET}")
    print(f"Total: {results['passed'] + results['failed']}")
    
    success_rate = (results['passed'] / (results['passed'] + results['failed'])) * 100
    print(f"Success Rate: {success_rate:.1f}%")
    
    if results['failed'] == 0:
        print(f"\n{GREEN}{'='*80}{RESET}")
        print(f"{GREEN}🎉 ALL TESTS PASSED! 🎉{RESET}")
        print(f"{GREEN}{'='*80}{RESET}")
        return 0
    else:
        print(f"\n{YELLOW}Some tests failed. Review the output above for details.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
