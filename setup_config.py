#!/usr/bin/env python3
"""
Configuration helper for the Spike AI Hackathon project.
Run this to set up your environment variables.
"""

import os
import sys

def setup_config():
    """
    Interactive setup for configuration.
    """
    print("="*80)
    print("SPIKE AI HACKATHON - CONFIGURATION SETUP")
    print("="*80)
    
    config = {}
    
    # GA4 Property ID
    print("\n1. Google Analytics 4 Property ID")
    print("   Find this in GA4: Admin > Property Settings > Property ID")
    property_id = input("   Enter your GA4 Property ID: ").strip()
    config["GA4_PROPERTY_ID"] = property_id
    
    # LiteLLM API Key (already in .env, but verify)
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            if "LITELLM_API_KEY" in content:
                print("\n✓ LiteLLM API Key found in .env")
            else:
                print("\n⚠ LiteLLM API Key not found in .env")
                api_key = input("   Enter your LiteLLM API Key: ").strip()
                with open(env_file, 'a') as f:
                    f.write(f"\nLITELLM_API_KEY={api_key}\n")
    else:
        print("\n⚠ .env file not found")
        api_key = input("   Enter your LiteLLM API Key: ").strip()
        with open(env_file, 'w') as f:
            f.write(f"LITELLM_API_KEY={api_key}\n")
    
    # credentials.json check
    print("\n2. Google Cloud Service Account Credentials")
    if os.path.exists("credentials.json"):
        print("   ✓ credentials.json found")
    else:
        print("   ⚠ credentials.json NOT FOUND")
        print("   Please place your GA4 service account credentials.json in the project root")
        print("   See setup instructions in README.md")
    
    # Update test_queries.py with property ID
    test_file = "test_queries.py"
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()
        
        updated_content = content.replace(
            'PROPERTY_ID = "YOUR_GA4_PROPERTY_ID"',
            f'PROPERTY_ID = "{property_id}"'
        )
        
        with open(test_file, 'w') as f:
            f.write(updated_content)
        
        print(f"\n✓ Updated {test_file} with your Property ID")
    
    # Update inject_traffic.py if needed
    print("\n3. Traffic Injection (Optional)")
    print("   Do you want to inject sample traffic data into your GA4 property?")
    inject = input("   This helps populate data for testing (y/n): ").strip().lower()
    
    if inject == 'y':
        print("\n   Please update inject_traffic.py with:")
        print(f"   - MEASUREMENT_ID: Your GA4 Measurement ID (G-XXXXXXXXXX)")
        print(f"   - API_SECRET: Your Measurement Protocol API secret")
        print(f"   Then run: python inject_traffic.py")
    
    print("\n" + "="*80)
    print("CONFIGURATION COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("1. Ensure credentials.json is in the project root")
    print("2. Run: bash deploy.sh")
    print("3. Test: python test_queries.py")
    print("\n" + "="*80)

if __name__ == "__main__":
    setup_config()
