#!/usr/bin/env python3
"""
Test script for OAuth token exchange and API calls
"""
import requests
import json
import sys

def test_oauth_flow(auth_code):
    """Test the complete OAuth flow with a real authorization code"""
    
    print("=== Testing OAuth Token Exchange ===")
    
    # Step 1: Exchange authorization code for access token
    token_url = "http://localhost:8081/oauth/token"
    params = {
        "code": auth_code,
        "redirect_uri": "http://localhost:8081/oauth/callback"
    }
    
    try:
        response = requests.post(token_url, params=params)
        print(f"Token exchange response status: {response.status_code}")
        print(f"Token exchange response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if access_token:
                print(f"\n=== Testing Protected Endpoints with Token ===")
                
                # Test user profile endpoint
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # Test user profile
                print("\n--- Testing User Profile ---")
                profile_response = requests.get("http://localhost:8081/user/profile", headers=headers)
                print(f"Profile response status: {profile_response.status_code}")
                print(f"Profile response: {profile_response.text}")
                
                # Test MLflow experiments
                print("\n--- Testing MLflow Experiments ---")
                experiments_response = requests.get("http://localhost:8081/mlflow/experiments", headers=headers)
                print(f"Experiments response status: {experiments_response.status_code}")
                print(f"Experiments response: {experiments_response.text}")
                
                return True
            else:
                print("No access token in response")
                return False
        else:
            print(f"Token exchange failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error during OAuth flow: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_oauth.py <authorization_code>")
        print("Get the authorization code from the OAuth callback URL")
        sys.exit(1)
    
    auth_code = sys.argv[1]
    success = test_oauth_flow(auth_code)
    
    if success:
        print("\n✅ OAuth flow test completed successfully!")
    else:
        print("\n❌ OAuth flow test failed!")
