#!/usr/bin/env python3
"""
Comprehensive robust testing script
Run this after the server is started with: bash deploy.sh
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8080"
PROPERTY_ID = "516812130"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")

print_header("🧪 COMPREHENSIVE ROBUST TESTING")

# Track results
results = {"passed": 0, "failed": 0, "errors": []}

def test_query(name, payload, expected_keys=None):
    """Test a single query"""
    print(f"\n{Colors.BOLD}{name}{Colors.END}")
    print(f"  Query: {payload.get('query', 'N/A')[:70]}...")
    
    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/query", json=payload, timeout=90)
        elapsed = time.time() - start
        
        print(f"  Status: {response.status_code} | Time: {elapsed:.2f}s")
        
        if response.status_code != 200:
            print(f"  {Colors.RED}❌ Failed: HTTP {response.status_code}{Colors.END}")
            results["failed"] += 1
            results["errors"].append(f"{name}: HTTP {response.status_code}")
            return False
        
        result = response.json()
        
        # Check for error in response
        if "error" in result:
            error_msg = result['error'][:120]
            print(f"  {Colors.YELLOW}⚠️  Error: {error_msg}{Colors.END}")
            results["failed"] += 1
            results["errors"].append(f"{name}: {error_msg}")
            return False
        
        # Check expected keys
        if expected_keys:
            missing = [k for k in expected_keys if k not in result]
            if missing:
                print(f"  {Colors.YELLOW}⚠️  Missing keys: {missing}{Colors.END}")
        
        # Check answer
        if "answer" in result:
            answer = result["answer"][:120]
            print(f"  {Colors.GREEN}✅ Answer: {answer}...{Colors.END}")
            
        # Check data
        if "data" in result:
            data = result["data"]
            if isinstance(data, list):
                print(f"  {Colors.GREEN}✅ Data: {len(data)} records{Colors.END}")
            else:
                print(f"  {Colors.GREEN}✅ Data: present{Colors.END}")
        
        results["passed"] += 1
        return True
        
    except requests.exceptions.Timeout:
        print(f"  {Colors.RED}❌ Timeout (>90s){Colors.END}")
        results["failed"] += 1
        results["errors"].append(f"{name}: Timeout")
        return False
    except Exception as e:
        error_msg = str(e)[:120]
        print(f"  {Colors.RED}❌ Error: {error_msg}{Colors.END}")
        results["failed"] += 1
        results["errors"].append(f"{name}: {error_msg}")
        return False

# Step 1: Health Check
print_header("STEP 1: SERVER HEALTH CHECK")

try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        health = response.json()
        print(f"{Colors.GREEN}✅ Server is healthy{Colors.END}")
        print(f"   Status: {health.get('status')}")
        print(f"   Credentials: {health.get('credentials')}")
        print(f"   Env loaded: {health.get('env_loaded')}")
    else:
        print(f"{Colors.RED}❌ Health check returned {response.status_code}{Colors.END}")
        sys.exit(1)
except Exception as e:
    print(f"{Colors.RED}❌ Server health check failed: {e}{Colors.END}")
    print(f"\n{Colors.YELLOW}Please restart the server first:{Colors.END}")
    print("   bash deploy.sh")
    sys.exit(1)

time.sleep(2)

# Step 2: Tier 1 - Analytics Agent Tests
print_header("STEP 2: TIER 1 - ANALYTICS AGENT (GA4)")

test_query(
    "T1.1: Simple user count",
    {"propertyId": PROPERTY_ID, "query": "How many users visited in the last 7 days?"},
    ["answer"]
)
time.sleep(3)

test_query(
    "T1.2: Page views",
    {"propertyId": PROPERTY_ID, "query": "Total page views for the last 30 days"},
    ["answer"]
)
time.sleep(3)

test_query(
    "T1.3: Daily breakdown",
    {"propertyId": PROPERTY_ID, "query": "Give me a daily breakdown of sessions for last 7 days"},
    ["answer", "data"]
)
time.sleep(3)

test_query(
    "T1.4: Traffic sources",
    {"propertyId": PROPERTY_ID, "query": "What are the top 5 traffic sources?"},
    ["answer"]
)
time.sleep(3)

# Step 3: Tier 2 - SEO Agent Tests
print_header("STEP 3: TIER 2 - SEO AGENT (SCREAMING FROG)")

test_query(
    "T2.1: Count URLs",
    {"query": "How many URLs are in the dataset?"},
    ["answer"]
)
time.sleep(3)

test_query(
    "T2.2: HTTPS filtering",
    {"query": "Which URLs do not use HTTPS?"},
    ["answer", "data"]
)
time.sleep(3)

test_query(
    "T2.3: Status code grouping",
    {"query": "Group all URLs by status code and count them"},
    ["answer", "data"]
)
time.sleep(3)

test_query(
    "T2.4: Content type analysis",
    {"query": "What content types are present in the data?"},
    ["answer"]
)
time.sleep(3)

# Step 4: Tier 3 - Multi-Agent Fusion Tests
print_header("STEP 4: TIER 3 - MULTI-AGENT FUSION")

test_query(
    "T3.1: Analytics + SEO fusion",
    {"propertyId": PROPERTY_ID, "query": "What are the top 5 pages by views with their status codes?"},
    ["answer"]
)
time.sleep(3)

test_query(
    "T3.2: JSON output request",
    {"propertyId": PROPERTY_ID, "query": "Return the top 3 pages by views in JSON format"},
    ["data"]
)
time.sleep(3)

# Step 5: Edge Cases & Error Handling
print_header("STEP 5: EDGE CASES & ERROR HANDLING")

# Test missing propertyId
print(f"\n{Colors.BOLD}E1: Missing propertyId{Colors.END}")
print("  Query: Analytics query without propertyId")
try:
    response = requests.post(
        f"{BASE_URL}/query",
        json={"query": "How many users last 7 days?"},
        timeout=30
    )
    result = response.json()
    if "error" in result and "property" in result["error"].lower():
        print(f"  {Colors.GREEN}✅ Correctly rejected query without propertyId{Colors.END}")
        results["passed"] += 1
    else:
        print(f"  {Colors.YELLOW}⚠️  Should require propertyId for analytics queries{Colors.END}")
        results["failed"] += 1
except Exception as e:
    print(f"  {Colors.RED}❌ Error: {e}{Colors.END}")
    results["failed"] += 1

time.sleep(2)

test_query(
    "E2: Invalid propertyId",
    {"propertyId": "999999999", "query": "How many users?"}
)
time.sleep(2)

test_query(
    "E3: Empty query",
    {"propertyId": PROPERTY_ID, "query": ""}
)
time.sleep(2)

test_query(
    "E4: Ambiguous query",
    {"query": "Give me some data"}
)

# Final Summary
print_header("TEST RESULTS SUMMARY")

total = results["passed"] + results["failed"]
success_rate = (results["passed"] / total * 100) if total > 0 else 0

print(f"\n{Colors.BOLD}Total Tests: {total}{Colors.END}")
print(f"{Colors.GREEN}✅ Passed: {results['passed']}{Colors.END}")
print(f"{Colors.RED}❌ Failed: {results['failed']}{Colors.END}")
print(f"{Colors.BOLD}📊 Success Rate: {success_rate:.1f}%{Colors.END}\n")

if results["errors"]:
    print(f"{Colors.YELLOW}Errors encountered:{Colors.END}")
    for i, error in enumerate(results["errors"][:10], 1):
        print(f"  {i}. {error}")

print("\n" + "="*80)
if success_rate >= 80:
    print(f"{Colors.GREEN}{Colors.BOLD}🎉 EXCELLENT! Project passes robust testing and is ready for submission!{Colors.END}")
elif success_rate >= 60:
    print(f"{Colors.GREEN}✅ GOOD! Most tests passing, minor improvements possible{Colors.END}")
else:
    print(f"{Colors.YELLOW}⚠️  NEEDS ATTENTION: Multiple tests failing, check errors above{Colors.END}")

print("="*80 + "\n")
