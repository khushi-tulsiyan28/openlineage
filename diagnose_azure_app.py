#!/usr/bin/env python3
"""
Diagnose Azure App Registration issues
"""
import requests
import json

def test_app_registration():
    """Test various aspects of the app registration"""
    
    print("=== Azure App Registration Diagnostic ===")
    
    # Test 1: Check if we can get a token using client credentials flow
    print("\n1. Testing Client Credentials Flow (no user interaction)")
    
    token_url = "https://login.microsoftonline.com/5f892d7b-6294-4f75-aa09-20fb450b9bf2/oauth2/v2.0/token"
    
    client_credentials_data = {
        "client_id": "1c3c2a07-a8a5-4358-883f-9030f73125e3",
        "client_secret": "821236ef-db35-4c48-b5e9-9161190eef72",
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(token_url, data=client_credentials_data)
        print(f"Client Credentials Status: {response.status_code}")
        print(f"Client Credentials Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Client credentials flow works - app registration is valid")
            return True
        else:
            print("❌ Client credentials flow failed - app registration issue")
            
    except Exception as e:
        print(f"❌ Error in client credentials test: {e}")
    
    # Test 2: Check authorization endpoint
    print("\n2. Testing Authorization Endpoint")
    
    auth_url = "https://login.microsoftonline.com/5f892d7b-6294-4f75-aa09-20fb450b9bf2/oauth2/v2.0/authorize"
    auth_params = {
        "client_id": "1c3c2a07-a8a5-4358-883f-9030f73125e3",
        "response_type": "code",
        "redirect_uri": "http://localhost:8081/oauth/callback",
        "scope": "openid profile email",
        "response_mode": "query"
    }
    
    try:
        response = requests.get(auth_url, params=auth_params, allow_redirects=False)
        print(f"Authorization Status: {response.status_code}")
        print(f"Authorization Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("✅ Authorization endpoint works - redirects to login")
        else:
            print("❌ Authorization endpoint issue")
            
    except Exception as e:
        print(f"❌ Error in authorization test: {e}")
    
    return False

def check_common_issues():
    """Check for common configuration issues"""
    
    print("\n=== Common Issues Checklist ===")
    
    issues = [
        "1. Redirect URI 'http://localhost:8081/oauth/callback' must be registered in Azure App Registration",
        "2. Client secret must not be expired (check in Azure Portal)",
        "3. App registration must have 'Web' platform configured",
        "4. API permissions must include 'openid', 'profile', 'email'",
        "5. Admin consent may be required for some permissions",
        "6. Authorization code may have expired (they expire quickly)",
        "7. Make sure you're using the correct tenant ID"
    ]
    
    for issue in issues:
        print(f"   {issue}")
    
    print("\n=== Recommended Actions ===")
    print("1. Go to Azure Portal → App registrations → Your app")
    print("2. Check Authentication → Redirect URIs")
    print("3. Check Certificates & secrets → Client secrets")
    print("4. Check API permissions → Microsoft Graph")
    print("5. Try creating a new client secret if current one is expired")

if __name__ == "__main__":
    success = test_app_registration()
    check_common_issues()
    
    if not success:
        print("\n❌ App registration has issues that need to be fixed in Azure Portal")
    else:
        print("\n✅ App registration appears to be working correctly")
