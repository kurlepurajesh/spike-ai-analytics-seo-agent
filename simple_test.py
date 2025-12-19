import requests
import time

BASE = "http://localhost:8080"
PID = "516812130"

tests = []

# Test 1: Health
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    tests.append(("Health Check", r.status_code == 200))
except:
    tests.append(("Health Check", False))

# Test 2: Analytics
try:
    r = requests.post(f"{BASE}/query", json={"query": "Sessions last 7 days", "propertyId": PID}, timeout=20)
    data = r.json()
    tests.append(("Analytics Agent", all(k in data for k in ['answer','data','thought_process'])))
except:
    tests.append(("Analytics Agent", False))

# Test 3: SEO
try:
    r = requests.post(f"{BASE}/query", json={"query": "Count URLs", "propertyId": PID}, timeout=20)
    data = r.json()
    tests.append(("SEO Agent", 'data' in data))
except:
    tests.append(("SEO Agent", False))

# Test 4: SEO Filtering
try:
    r = requests.post(f"{BASE}/query", json={"query": "URLs not using HTTPS", "propertyId": PID}, timeout=25)
    data = r.json()
    tests.append(("SEO Filtering", len(data.get('data', [])) == 1))
except:
    tests.append(("SEO Filtering", False))

# Test 5: JSON Output
try:
    r = requests.post(f"{BASE}/query", json={"query": "Return 3 URLs in JSON", "propertyId": PID}, timeout=25)
    data = r.json()
    tests.append(("JSON Output", 'data' in data and 'answer' not in data))
except:
    tests.append(("JSON Output", False))

# Test 6: Error Handling
try:
    r = requests.post(f"{BASE}/query", json={"query": "Show data", "propertyId": "INVALID"}, timeout=25)
    tests.append(("Error Handling", r.status_code in [200, 400]))
except:
    tests.append(("Error Handling", False))

# Test 7: Intent - Analytics
try:
    r = requests.post(f"{BASE}/query", json={"query": "Sessions yesterday", "propertyId": PID}, timeout=20)
    data = r.json()
    tests.append(("Intent Detection", 'thought_process' in data))
except:
    tests.append(("Intent Detection", False))

# Summary
print("="*60)
print("TEST SUMMARY")
print("="*60)
passed = 0
for name, result in tests:
    status = "PASS" if result else "FAIL"
    print(f"{status} - {name}")
    if result:
        passed += 1

print("="*60)
print(f"Results: {passed}/{len(tests)} tests passed")
print("="*60)
