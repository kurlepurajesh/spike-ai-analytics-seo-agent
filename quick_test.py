#!/usr/bin/env python3
import requests, time

print("🧪 QUICK TEST\n" + "="*60)

r = []

def t(n, p):
    print(f"\n{n}")
    try:
        res = requests.post("http://localhost:8080/query", json=p, timeout=40)
        d = res.json()
        if "answer" in d:
            print(f"✅ {d['answer'][:70]}")
            r.append(1)
        elif "error" in d:
            print(f"❌ {d['error'][:70]}")
            r.append(0)
        else:
            print("❌ No response")
            r.append(0)
    except Exception as e:
        print(f"❌ {e}")
        r.append(0)
    time.sleep(2)

t("Analytics", {"propertyId": "516812130", "query": "Users last 7 days?"})
t("SEO", {"query": "How many URLs?"})
t("Fusion", {"propertyId": "516812130", "query": "Top pages with status"})

print(f"\n{'='*60}")
print(f"Result: {sum(r)}/{len(r)} passed ({sum(r)/len(r)*100:.0f}%)")
print(f"{'='*60}")
