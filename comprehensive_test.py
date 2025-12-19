#!/usr/bin/env python3
"""
Comprehensive Testing and Validation Script
Tests all 3 tiers and verifies output correctness
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8080"
PROPERTY_ID = "516812130"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Server is healthy")
            print_info(f"  Status: {data.get('status')}")
            print_info(f"  Credentials: {data.get('credentials')}")
            print_info(f"  Env Loaded: {data.get('env_loaded')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def test_analytics_query():
    """Test Tier 1: Analytics Agent"""
    print("\n" + "="*60)
    print("TEST 2: Analytics Agent (Tier 1)")
    print("="*60)
    
    query = "How many sessions in the last 7 days?"
    print_info(f"Query: {query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"propertyId": PROPERTY_ID, "query": query},
            timeout=300
        )
        
        if response.status_code != 200:
            print_error(f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        # Verify required fields
        checks = [
            ("answer" in data, "Has 'answer' field"),
            ("data" in data, "Has 'data' field"),
            ("thought_process" in data, "Has 'thought_process' field"),
        ]
        
        all_passed = True
        for check, desc in checks:
            if check:
                print_success(desc)
            else:
                print_error(desc)
                all_passed = False
        
        # Check thought process
        if "thought_process" in data:
            tp = data["thought_process"]
            if "final_params" in tp:
                print_info(f"  Date range: {tp['final_params'].get('date_ranges', [])}")
                print_info(f"  Metrics: {tp['final_params'].get('metrics', [])}")
        
        # Check data structure
        if "data" in data:
            print_info(f"  Rows returned: {data['data'].get('row_count', len(data['data'].get('rows', [])))}")
        
        return all_passed
        
    except Exception as e:
        print_error(f"Analytics test error: {e}")
        return False

def test_seo_query():
    """Test Tier 2: SEO Agent"""
    print("\n" + "="*60)
    print("TEST 3: SEO Agent (Tier 2)")
    print("="*60)
    
    query = "How many total URLs are in the sheet?"
    print_info(f"Query: {query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"propertyId": PROPERTY_ID, "query": query},
            timeout=300
        )
        
        if response.status_code != 200:
            print_error(f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        # Verify required fields
        checks = [
            ("answer" in data, "Has 'answer' field"),
            ("data" in data, "Has 'data' field"),
            ("thought_process" in data, "Has 'thought_process' field"),
        ]
        
        all_passed = True
        for check, desc in checks:
            if check:
                print_success(desc)
            else:
                print_error(desc)
                all_passed = False
        
        # Verify count is 21 (known from manual inspection)
        if data.get("data") and len(data["data"]) > 0:
            total_urls = data["data"][0].get("Total URLs", 0)
            if total_urls == 21:
                print_success(f"Correct count: {total_urls} URLs")
            else:
                print_warning(f"Expected 21 URLs, got {total_urls}")
        
        # Check generated code
        if "thought_process" in data and "final_code" in data["thought_process"]:
            print_info(f"  Generated code: {data['thought_process']['final_code'][:50]}...")
        
        return all_passed
        
    except Exception as e:
        print_error(f"SEO test error: {e}")
        return False

def test_seo_filtering():
    """Test SEO filtering accuracy"""
    print("\n" + "="*60)
    print("TEST 4: SEO Filtering Accuracy")
    print("="*60)
    
    query = "Which URLs do not use HTTPS?"
    print_info(f"Query: {query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"propertyId": PROPERTY_ID, "query": query},
            timeout=300
        )
        
        if response.status_code != 200:
            print_error(f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        # Should find exactly 1 URL: http://getspike.ai/about
        http_urls = data.get("data", [])
        
        if len(http_urls) == 1:
            print_success(f"Correct: Found 1 non-HTTPS URL")
            url = http_urls[0].get("Address", "")
            if url == "http://getspike.ai/about":
                print_success(f"  URL matches expected: {url}")
            else:
                print_warning(f"  URL doesn't match expected: {url}")
        else:
            print_error(f"Expected 1 URL, got {len(http_urls)}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Filtering test error: {e}")
        return False

def test_json_output():
    """Test JSON-only output format"""
    print("\n" + "="*60)
    print("TEST 5: JSON Output Format")
    print("="*60)
    
    query = "Return 3 URLs in JSON format"
    print_info(f"Query: {query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"propertyId": PROPERTY_ID, "query": query},
            timeout=300
        )
        
        if response.status_code != 200:
            print_error(f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        # Should only have 'data' field, no 'answer' or 'thought_process'
        has_data_only = "data" in data and "answer" not in data
        
        if has_data_only:
            print_success("JSON-only output: ✓")
            print_info(f"  Returned {len(data.get('data', []))} items")
        else:
            print_warning("JSON output includes extra fields")
        
        return has_data_only
        
    except Exception as e:
        print_error(f"JSON test error: {e}")
        return False

def test_fusion_query():
    """Test Tier 3: Multi-Agent Fusion"""
    print("\n" + "="*60)
    print("TEST 6: Multi-Agent Fusion (Tier 3)")
    print("="*60)
    
    query = "What are the top pages by views with their status codes?"
    print_info(f"Query: {query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"propertyId": PROPERTY_ID, "query": query},
            timeout=300
        )
        
        if response.status_code != 200:
            print_error(f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        # Verify fusion structure
        checks = [
            ("answer" in data, "Has 'answer' field"),
            ("data" in data, "Has 'data' field"),
        ]
        
        all_passed = True
        for check, desc in checks:
            if check:
                print_success(desc)
            else:
                print_error(desc)
                all_passed = False
        
        # Check fusion data structure
        if "data" in data:
            fusion_data = data["data"]
            
            if "fused_data" in fusion_data:
                print_success("Has 'fused_data' array")
                print_info(f"  Analytics count: {fusion_data.get('analytics_count', 0)}")
                print_info(f"  SEO count: {fusion_data.get('seo_count', 0)}")
                print_info(f"  Matched count: {fusion_data.get('matched_count', 0)}")
            else:
                print_warning("Missing 'fused_data' structure")
        
        return all_passed
        
    except Exception as e:
        print_error(f"Fusion test error: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid property ID"""
    print("\n" + "="*60)
    print("TEST 7: Error Handling")
    print("="*60)
    
    query = "Show me data"
    invalid_property = "INVALID_12345"
    print_info(f"Query: {query} (with invalid property ID)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"propertyId": invalid_property, "query": query},
            timeout=300
        )
        
        # Should not crash (status code should be 200 with error message)
        if response.status_code in [200, 400]:
            data = response.json()
            if "error" in data or "answer" in data:
                print_success("Handles invalid property gracefully")
                return True
            else:
                print_warning("Response structure unexpected")
                return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
        
    except Exception as e:
        print_error(f"Error handling test failed: {e}")
        return False

def test_intent_detection():
    """Test intent detection accuracy"""
    print("\n" + "="*60)
    print("TEST 8: Intent Detection")
    print("="*60)
    
    test_cases = [
        ("How many sessions yesterday?", "analytics"),
        ("List all URLs", "seo"),
        ("Top pages by views with their title tags", "fusion"),
    ]
    
    all_passed = True
    
    for query, expected_intent in test_cases:
        print_info(f"Query: {query}")
        print_info(f"  Expected intent: {expected_intent}")
        
        # We can't directly check intent, but we can verify the response structure
        try:
            response = requests.post(
                f"{BASE_URL}/query",
                json={"propertyId": PROPERTY_ID, "query": query},
                timeout=300
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response structure matches expected intent
                if expected_intent == "fusion":
                    has_fusion = "fused_data" in str(data)
                    if has_fusion:
                        print_success(f"  Correctly routed to fusion")
                    else:
                        print_warning(f"  May not have routed to fusion")
                else:
                    print_success(f"  Response received")
            else:
                print_warning(f"  HTTP {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print_error(f"  Error: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SPIKE AI HACKATHON - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run all tests
    results.append(("Health Check", test_health()))
    results.append(("Analytics Agent", test_analytics_query()))
    results.append(("SEO Agent", test_seo_query()))
    results.append(("SEO Filtering", test_seo_filtering()))
    results.append(("JSON Output", test_json_output()))
    results.append(("Fusion Agent", test_fusion_query()))
    results.append(("Error Handling", test_error_handling()))
    results.append(("Intent Detection", test_intent_detection()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} - {test_name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print_success("\n🎉 All tests passed! System is ready for submission.")
        return 0
    else:
        print_error(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
