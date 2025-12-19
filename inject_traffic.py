import requests
import json
import time
import random
from datetime import datetime, timedelta

# Configuration
MEASUREMENT_ID = "G-TCW5H4LF7G"
API_SECRET = "9FhVOVM6RTqLthRwuz_Gtg"
CLIENT_ID = "555.555"  # Fake client ID

# GA4 Measurement Protocol Endpoint
URL = f"https://www.google-analytics.com/mp/collect?measurement_id={MEASUREMENT_ID}&api_secret={API_SECRET}"

def send_event(event_name, params=None, timestamp_micros=None):
    payload = {
        "client_id": CLIENT_ID,
        "events": [{
            "name": event_name,
            "params": params or {}
        }]
    }
    
    # Add timestamp for backdating if provided
    if timestamp_micros:
        payload["timestamp_micros"] = int(timestamp_micros)

    response = requests.post(URL, json=payload)
    if response.status_code == 204:
        print(f"Successfully sent event: {event_name}")
    else:
        print(f"Failed to send event: {response.status_code} - {response.text}")

def inject_historical_data():
    print("Injecting data for the last 7 days...")
    
    # Generate data for the last 7 days
    for i in range(7):
        day_offset = 6 - i  # 6 days ago, 5 days ago, ... 0 days ago
        date = datetime.now() - timedelta(days=day_offset)
        
        # Convert to microseconds for GA4 timestamp
        timestamp_micros = date.timestamp() * 1_000_000
        
        # Random number of users per day (5-15)
        users_count = random.randint(5, 15)
        
        print(f"Injecting {users_count} users for {date.strftime('%Y-%m-%d')}...")
        
        for _ in range(users_count):
            # Unique client ID for each "user" to count as separate active users
            unique_client_id = f"{random.randint(100000, 999999)}.{random.randint(100000, 999999)}"
            
            payload = {
                "client_id": unique_client_id,
                "timestamp_micros": int(timestamp_micros),
                "events": [
                    {
                        "name": "page_view",
                        "params": {
                            "page_location": "https://example.com/home",
                            "page_title": "Home Page"
                        }
                    },
                    {
                        "name": "session_start",
                        "params": {}
                    }
                ]
            }
            
            requests.post(URL, json=payload)
            time.sleep(0.05) # Slight delay

    print("Data injection complete! Note: It may take 24-48 hours for standard reports to update, but Realtime should show recent activity.")

    print("Injecting LIVE traffic for Realtime API verification...")
    # Inject current traffic for Realtime API
    for _ in range(5):
        unique_client_id = f"{random.randint(100000, 999999)}.{random.randint(100000, 999999)}"
        payload = {
            "client_id": unique_client_id,
            "timestamp_micros": int(datetime.now().timestamp() * 1_000_000),
            "events": [
                {
                    "name": "page_view",
                    "params": {
                        "page_location": "https://example.com/realtime-test",
                        "page_title": "Realtime Test Page"
                    }
                }
            ]
        }
        requests.post(URL, json=payload)
        time.sleep(0.1)
    print("Live traffic injected!")

if __name__ == "__main__":
    inject_historical_data()
