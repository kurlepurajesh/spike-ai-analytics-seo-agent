#!/bin/bash
echo "=== TEST 1: Health Check ==="
curl -s http://localhost:8080/health | python3 -m json.tool

echo -e "\n\n=== TEST 2: Analytics (will show no data - expected) ==="
curl -s -X POST http://localhost:8080/query -H "Content-Type: application/json" -d '{"query": "Total sessions last 7 days", "propertyId": "516812130"}' | python3 -c "import sys, json; r=json.load(sys.stdin); print(f\"✓ Status: {'OK' if 'answer' in r else 'FAIL'}\")"

echo -e "\n=== TEST 3: SEO Query ==="
curl -s -X POST http://localhost:8080/query -H "Content-Type: application/json" -d '{"query": "How many URLs in total?", "propertyId": "516812130"}' | python3 -c "import sys, json; r=json.load(sys.stdin); print(f\"✓ URLs found: {r.get('data', [{}])[0].get('Total URLs', 0)}\")"

echo -e "\n=== TEST 4: JSON Format ==="
curl -s -X POST http://localhost:8080/query -H "Content-Type: application/json" -d '{"query": "Get 3 blog URLs in JSON format", "propertyId": "516812130"}' | python3 -c "import sys, json; r=json.load(sys.stdin); print(f\"✓ JSON entries: {len(r.get('data', []))}\")"

echo -e "\n=== TEST 5: Complex SEO Query ==="
curl -s -X POST http://localhost:8080/query -H "Content-Type: application/json" -d '{"query": "Show addresses and status codes for pricing and careers pages", "propertyId": "516812130"}' | python3 -c "import sys, json; r=json.load(sys.stdin); print(f\"✓ Results: {len(r.get('data', []))} rows\")"

echo -e "\n✅ All tests completed!"
