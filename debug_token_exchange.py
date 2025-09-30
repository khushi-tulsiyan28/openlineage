#!/usr/bin/env python3
"""
Debug token exchange with detailed error reporting
"""
import requests
import json

def debug_token_exchange(auth_code):
    """Debug the token exchange process with detailed error reporting"""
    
    print("=== Debugging Token Exchange ===")
    print(f"Authorization Code: {auth_code[:50]}...")
    
    # Test the token exchange endpoint
    token_url = "http://localhost:8081/oauth/token"
    params = {
        "code": auth_code,
        "redirect_uri": "http://localhost:8081/oauth/callback"
    }
    
    print(f"Token URL: {token_url}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.post(token_url, params=params)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code != 200:
            print(f"\n❌ Token exchange failed with status {response.status_code}")
            return False
        else:
            print(f"\n✅ Token exchange successful!")
            token_data = response.json()
            print(f"Token Data: {json.dumps(token_data, indent=2)}")
            return True
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return False

def test_direct_microsoft_token_exchange(auth_code):
    """Test token exchange directly with Microsoft"""
    
    print("\n=== Testing Direct Microsoft Token Exchange ===")
    
    token_url = "https://login.microsoftonline.com/5f892d7b-6294-4f75-aa09-20fb450b9bf2/oauth2/v2.0/token"
    
    data = {
        "client_id": "1c3c2a07-a8a5-4358-883f-9030f73125e3",
        "client_secret": "821236ef-db35-4c48-b5e9-9161190eef72",
        "code": auth_code,
        "redirect_uri": "http://localhost:8081/oauth/callback",
        "grant_type": "authorization_code"
    }
    
    print(f"Direct Token URL: {token_url}")
    print(f"Request Data: {data}")
    
    try:
        response = requests.post(token_url, data=data)
        print(f"\nDirect Response Status: {response.status_code}")
        print(f"Direct Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Direct token exchange successful!")
            return True
        else:
            print(f"❌ Direct token exchange failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during direct token exchange: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python debug_token_exchange.py <authorization_code>")
        sys.exit(1)
    
    auth_code = sys.argv[1]
    
    # Test through API gateway
    success1 = debug_token_exchange(auth_code)
    
    # Test directly with Microsoft
    success2 = test_direct_microsoft_token_exchange(auth_code)
    
    if success1 or success2:
        print("\n✅ At least one token exchange method worked!")
    else:
        print("\n❌ Both token exchange methods failed!")
