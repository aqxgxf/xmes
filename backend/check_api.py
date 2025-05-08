#!/usr/bin/env python
import sys
import os
import requests
import json

# Path setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration
API_BASE_URL = "http://localhost:8900"  # Adjust if your server is running on a different port

def check_workorders_api():
    """Check the /api/workorders/ endpoint response format"""
    url = f"{API_BASE_URL}/api/workorders/"
    
    print(f"Making GET request to {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        print(f"Status code: {response.status_code}")
        data = response.json()
        
        print("\nResponse structure:")
        print(json.dumps(data if not isinstance(data, list) else {"type": "list", "length": len(data)}, indent=2))
        
        if isinstance(data, list):
            print(f"\nFound {len(data)} workorders in array format")
        elif isinstance(data, dict):
            if "results" in data:
                print(f"\nFound {len(data['results'])} workorders in paginated format")
                print(f"Total count: {data.get('count', 'unknown')}")
            elif "data" in data:
                if isinstance(data["data"], list):
                    print(f"\nFound {len(data['data'])} workorders in custom data format")
                elif "results" in data["data"]:
                    print(f"\nFound {len(data['data']['results'])} workorders in nested paginated format")
                    print(f"Total count: {data['data'].get('count', 'unknown')}")
            else:
                print("\nUnknown dictionary response format")
        else:
            print("\nUnknown response format")
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON response")
        print("Raw response:")
        print(response.text[:1000])  # Show first 1000 chars
        
if __name__ == "__main__":
    check_workorders_api() 