#!/usr/bin/env python3
"""
Comprehensive Test with Output Validation
Tests all 3 tiers and validates response quality
"""

import requests
import json
import time
from datetime import datetime

PROPERTY_ID = "516812130"
BASE_URL = "http://localhost:8080"

# Color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

test_results = []

def validate_and_test(test_name, payload, expected_keywords=None, tier=""):
    """Run test and validate output quality"""
    print(f"\n{'='*80}")
    print(f"{BOLD}{tier}TEST: {test_name}{RESET}")
    print(f"{'='*80}")
    print(f"Query: {BLUE}{payload.get('query')}{RESET}")
    if 'propertyId' in payload:
        print(f"PropertyId: {payload['propertyId']}")
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/query", json=payload, timeout=120)
        elapsed = time.time() - start_time
        
        print(f"Response Time: {elapsed:.2f}s")
        print(f"HTTP Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"{RED}❌ FAIL: HTTP {response.status_code}{RESET}")
            print(f"Response: {response.text[:200]}")
            test_results.append({
                "test": test_name,
                "status": "FAIL",
                "reason": f"HTTP {response.status_code}",
                "elapsed": elapsed
            })
            return False
        
        result = response.json()
        
        # Check for errors
        if "error" in result:
            print(f"{RED}❌ FAIL: {result['error']}{RESET}")
            test_results.append({
                "test": test_name,
                "status": "FAIL",
                "reason": result['error'],
                "elapsed": elapsed
            })
            return False
        
        # Extract answer and data
        has_answer = "answer" in result
        has_data = "data" in result
        
        print(f"\n{BOLD}Response Structure:{RESET}")
        print(f"  - Has 'answer': {GREEN if has_answer else RED}{has_answer}{RESET}")
        print(f"  - Has 'data': {GREEN if has_data else RED}{has_data}{RESET}")
        
        if not has_answer:
            print(f"{RED}❌ FAIL: No 'answer' field in response{RESET}")
            test_results.append({
                "test": test_name,
                "status": "FAIL",
                "reason": "Missing 'answer' field",
                "elapsed": elapsed
            })
            return False
        
        answer = result['answer']
        answer_len = len(answer)
        
        print(f"\n{BOLD}📝 ANSWER ({answer_len} chars):{RESET}")
        print(f"{answer}")
        
        # Quality validations
        validations = []
        quality_score = 0
        
        # 1. Length check
        if answer_len > 50:
            validations.append(f"{GREEN}✅ Substantial answer ({answer_len} chars){RESET}")
            quality_score += 1
        elif answer_len > 20:
            validations.append(f"{YELLOW}⚠️  Short answer ({answer_len} chars){RESET}")
        else:
            validations.append(f"{RED}❌ Answer too short ({answer_len} chars){RESET}")
        
        # 2. Not an error message
        error_indicators = ["error", "failed", "could not", "unable to"]
        has_error_words = any(indicator in answer.lower() for indicator in error_indicators)
        if not has_error_words:
            validations.append(f"{GREEN}✅ No error indicators{RESET}")
            quality_score += 1
        else:
            validations.append(f"{RED}❌ Contains error indicators{RESET}")
        
        # 3. Contains expected keywords
        if expected_keywords:
            found = []
            missing = []
            for keyword in expected_keywords:
                if keyword.lower() in answer.lower():
                    found.append(keyword)
                else:
                    missing.append(keyword)
            
            if found:
                validations.append(f"{GREEN}✅ Contains: {', '.join(found)}{RESET}")
                quality_score += 1
            if missing:
                validations.append(f"{YELLOW}⚠️  Missing keywords: {', '.join(missing)}{RESET}")
        
        # 4. Check for numerical data (for analytics/SEO queries)
        import re
        has_numbers = bool(re.search(r'\d+', answer))
        if has_numbers:
            validations.append(f"{GREEN}✅ Contains numerical data{RESET}")
            quality_score += 1
        else:
            validations.append(f"{YELLOW}⚠️  No numerical data found{RESET}")
        
        print(f"\n{BOLD}📊 Quality Validation:{RESET}")
        for v in validations:
            print(f"  {v}")
        
        # Data validation
        if has_data:
            data = result['data']
            if isinstance(data, list):
                print(f"\n{BOLD}📊 DATA VALIDATION:{RESET}")
                print(f"  - Type: List")
                print(f"  - Records: {GREEN}{len(data)}{RESET}")
                if len(data) > 0:
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        print(f"  - Keys: {', '.join(list(first_item.keys())[:5])}")
                        print(f"  - Sample: {json.dumps(first_item, indent=4)[:200]}...")
                    quality_score += 1
            else:
                print(f"\n{BOLD}📊 DATA:{RESET} {type(data).__name__}")
        
        # Overall assessment
        max_score = 5
        quality_pct = (quality_score / max_score) * 100
        
        print(f"\n{BOLD}Quality Score: {quality_score}/{max_score} ({quality_pct:.0f}%){RESET}")
        
        if quality_score >= 3:
            print(f"{GREEN}✅ PASS: High-quality response{RESET}")
            test_results.append({
                "test": test_name,
                "status": "PASS",
                "quality_score": quality_score,
                "answer_length": answer_len,
                "has_data": has_data,
                "elapsed": elapsed
            })
            return True
        elif quality_score >= 2:
            print(f"{YELLOW}⚠️  PARTIAL: Response present but quality issues{RESET}")
            test_results.append({
                "test": test_name,
                "status": "PARTIAL",
                "quality_score": quality_score,
                "elapsed": elapsed
            })
            return False
        else:
            print(f"{RED}❌ FAIL: Poor quality response{RESET}")
            test_results.append({
                "test": test_name,
                "status": "FAIL",
                "quality_score": quality_score,
                "elapsed": elapsed
            })
            return False
            
    except requests.exceptions.Timeout:
        print(f"{RED}❌ FAIL: Timeout (>60s){RESET}")
        test_results.append({
            "test": test_name,
            "status": "FAIL",
            "reason": "Timeout"
        })
        return False
    except Exception as e:
        print(f"{RED}❌ FAIL: {str(e)}{RESET}")
        test_results.append({
            "test": test_name,
            "status": "FAIL",
            "reason": str(e)
        })
        return False

def main():
    print(f"{BOLD}{'='*80}")
    print("🧪 COMPREHENSIVE TEST WITH OUTPUT VALIDATION")
    print(f"{'='*80}{RESET}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Property ID: {PROPERTY_ID}")
    
    # Check server health
    print(f"\n{BOLD}Checking server health...{RESET}")
    server_ready = False
    for i in range(5):
        try:
            health = requests.get(f"{BASE_URL}/health", timeout=10)
            if health.status_code == 200:
                print(f"{GREEN}✅ Server is up: {health.json()}{RESET}")
                server_ready = True
                break
        except Exception as e:
            print(f"{YELLOW}Attempt {i+1}/5 failed: {e}... retrying in 2s{RESET}")
            time.sleep(5)
    
    if not server_ready:
        print(f"{RED}❌ Server health check failed after 5 attempts.{RESET}")
        print("Please start the server first: bash deploy.sh")
        return
    
    # TIER 1: Analytics Tests
    print(f"\n{BLUE}{'='*80}")
    print("🔵 TIER 1: ANALYTICS AGENT TESTS")
    print(f"{'='*80}{RESET}")
    
    validate_and_test(
        "User Count (Last 7 Days)",
        {"propertyId": PROPERTY_ID, "query": "How many users visited the site in the last 7 days?"},
        expected_keywords=["user", "7", "days"],
        tier=f"{BLUE}[T1.1] {RESET}"
    )
    
    time.sleep(5)
    
    validate_and_test(
        "Page Views (Last 30 Days)",
        {"propertyId": PROPERTY_ID, "query": "What is the total number of page views in the last 30 days?"},
        expected_keywords=["page", "view", "30"],
        tier=f"{BLUE}[T1.2] {RESET}"
    )
    
    time.sleep(5)
    
    validate_and_test(
        "Sessions Per Device",
        {"propertyId": PROPERTY_ID, "query": "Show me sessions broken down by device category"},
        expected_keywords=["session", "device"],
        tier=f"{BLUE}[T1.3] {RESET}"
    )
    
    # TIER 2: SEO Tests
    print(f"\n{GREEN}{'='*80}")
    print("🟢 TIER 2: SEO AGENT TESTS")
    print(f"{'='*80}{RESET}")
    
    time.sleep(5)
    
    validate_and_test(
        "Total URL Count",
        {"query": "How many total URLs are in the dataset?"},
        expected_keywords=["url", "total"],
        tier=f"{GREEN}[T2.1] {RESET}"
    )
    
    time.sleep(5)
    
    validate_and_test(
        "HTTPS Check",
        {"query": "Which URLs do not use HTTPS?"},
        expected_keywords=["http", "url"],
        tier=f"{GREEN}[T2.2] {RESET}"
    )
    
    time.sleep(5)
    
    validate_and_test(
        "Status Code Distribution",
        {"query": "Group all URLs by their HTTP status code and give me the count for each"},
        expected_keywords=["status", "code"],
        tier=f"{GREEN}[T2.3] {RESET}"
    )
    
    # TIER 3: Fusion Tests
    print(f"\n{PURPLE}{'='*80}")
    print("🟣 TIER 3: MULTI-AGENT FUSION TESTS")
    print(f"{'='*80}{RESET}")
    
    time.sleep(5)
    
    validate_and_test(
        "Top Pages with SEO Status",
        {"propertyId": PROPERTY_ID, "query": "What are the top 5 pages by views and what are their HTTP status codes?"},
        expected_keywords=["page", "view", "status"],
        tier=f"{PURPLE}[T3.1] {RESET}"
    )
    
    # Error Handling
    print(f"\n{YELLOW}{'='*80}")
    print("🟡 ERROR HANDLING TEST")
    print(f"{'='*80}{RESET}")
    
    print(f"\n{BOLD}[E1] Testing Missing PropertyId Validation{RESET}")
    print(f"Query: How many users in the last week?")
    print(f"PropertyId: (none - should return error)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"query": "How many users in the last week?"},
            timeout=30
        )
        result = response.json()
        
        if "error" in result and "property" in result["error"].lower():
            print(f"{GREEN}✅ PASS: Correctly rejected with validation error{RESET}")
            print(f"Error message: {result['error']}")
            test_results.append({
                "test": "Missing PropertyId Validation",
                "status": "PASS"
            })
        else:
            print(f"{RED}❌ FAIL: Should require propertyId for analytics{RESET}")
            print(f"Response: {result}")
            test_results.append({
                "test": "Missing PropertyId Validation",
                "status": "FAIL",
                "reason": "Did not validate propertyId"
            })
    except Exception as e:
        print(f"{RED}❌ FAIL: {e}{RESET}")
        test_results.append({
            "test": "Missing PropertyId Validation",
            "status": "FAIL",
            "reason": str(e)
        })
    
    # Final Summary
    print(f"\n{BOLD}{'='*80}")
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*80}{RESET}")
    
    passed = sum(1 for r in test_results if r["status"] == "PASS")
    failed = sum(1 for r in test_results if r["status"] == "FAIL")
    partial = sum(1 for r in test_results if r["status"] == "PARTIAL")
    total = len(test_results)
    
    print(f"\n{BOLD}Results:{RESET}")
    print(f"  Total Tests: {total}")
    print(f"  {GREEN}✅ Passed: {passed}{RESET}")
    print(f"  {YELLOW}⚠️  Partial: {partial}{RESET}")
    print(f"  {RED}❌ Failed: {failed}{RESET}")
    
    success_rate = (passed/total*100) if total > 0 else 0
    print(f"\n{BOLD}📈 Success Rate: {success_rate:.1f}%{RESET}")
    
    # Detailed breakdown
    if failed > 0 or partial > 0:
        print(f"\n{BOLD}📋 Detailed Results:{RESET}")
        for r in test_results:
            if r["status"] == "PASS":
                status_icon = f"{GREEN}✅{RESET}"
            elif r["status"] == "PARTIAL":
                status_icon = f"{YELLOW}⚠️{RESET}"
            else:
                status_icon = f"{RED}❌{RESET}"
            
            elapsed_str = f" ({r['elapsed']:.1f}s)" if 'elapsed' in r else ""
            quality_str = f" [Quality: {r['quality_score']}/5]" if 'quality_score' in r else ""
            print(f"  {status_icon} {r['test']}: {r['status']}{elapsed_str}{quality_str}")
            
            if "reason" in r and r["status"] != "PASS":
                print(f"     └─ {RED}{r['reason']}{RESET}")
    
    # Final assessment
    print(f"\n{BOLD}{'='*80}")
    if success_rate >= 80:
        print(f"{GREEN}🎉 EXCELLENT! Project is production-ready{RESET}")
        print(f"{GREEN}   All core functionality validated with high-quality outputs{RESET}")
    elif success_rate >= 60:
        print(f"{YELLOW}✅ GOOD! Core functionality working{RESET}")
        print(f"{YELLOW}   Some outputs may need refinement{RESET}")
    else:
        print(f"{RED}⚠️  NEEDS ATTENTION: Multiple failures detected{RESET}")
        print(f"{RED}   Review failed tests and fix issues{RESET}")
    print(f"{'='*80}{RESET}")
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save report to file
    with open("validation_report.txt", "w") as f:
        f.write(f"Validation Report - {datetime.now()}\n")
        f.write(f"Success Rate: {success_rate:.1f}%\n")
        f.write(f"Passed: {passed}, Failed: {failed}, Partial: {partial}\n")
        for r in test_results:
            f.write(f"{r['status']}: {r['test']}\n")

if __name__ == "__main__":
    main()
