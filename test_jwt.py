#!/usr/bin/env python3
"""
Test JWT token validation and structure
"""
import jwt
import requests
import json
from urllib.parse import urlparse, parse_qs

def test_jwt_validation():
    """Test JWT token validation logic"""
    
    print("=== Testing JWT Validation Logic ===")
    
    # Test with various token formats
    test_tokens = [
        "invalid_token",
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.invalid",
        "Bearer invalid_token",
        ""
    ]
    
    for token in test_tokens:
        print(f"\nTesting token: {token[:20]}...")
        
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        try:
            response = requests.get("http://localhost:8081/user/profile", headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

def extract_auth_code_from_url(url):
    """Extract authorization code from callback URL"""
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    return query_params.get('code', [None])[0]

if __name__ == "__main__":
    print("JWT Validation Test")
    print("==================")
    test_jwt_validation()
    
    print("\n" + "="*50)
    print("To test with real token:")
    print("1. Complete OAuth flow in browser")
    print("2. Copy the 'code' parameter from callback URL")
    print("3. Run: python test_oauth.py <code>")
