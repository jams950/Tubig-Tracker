#!/usr/bin/env python
"""
Simple script to test the API endpoint
"""
import requests
import json

def test_api():
    try:
        # Test the API endpoint
        url = "http://127.0.0.1:8000/api/all-complaints/"
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Number of reports: {len(data)}")
            
            if data:
                print("\nFirst report:")
                print(json.dumps(data[0], indent=2))
            else:
                print("No reports found")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_api()