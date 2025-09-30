#!/usr/bin/env python3
"""
Test script to simulate new user OAuth flow
"""
import requests
import json

def test_new_user_flow():
    """Test the OAuth flow for the new user testEx@techdwarfs.com"""
    
    print("🧪 Testing OAuth flow for new user: testEx@techdwarfs.com")
    print("")
    
    # Step 1: Get authorization URL
    print("1️⃣ Getting authorization URL...")
    try:
        response = requests.get("http://localhost:8081/oauth/authorize")
        auth_data = response.json()
        auth_url = auth_data.get('authorization_url')
        print(f"✅ Authorization URL: {auth_url}")
        print("")
        print("📋 To complete the test:")
        print("1. Visit the URL above in a browser")
        print("2. Sign in with testEx@techdwarfs.com")
        print("3. Complete OAuth flow")
        print("4. Copy the access_token from the response")
        print("5. Use it to test the /oauth/me endpoint")
        print("")
        
    except Exception as e:
        print(f"❌ Error getting authorization URL: {e}")
        return
    
    # Step 2: Test what the new user should see
    print("2️⃣ Expected behavior for testEx@techdwarfs.com:")
    print("   - Should see experiments 3 & 4 (Fraud Detection, Recommendation Engine)")
    print("   - Should NOT see experiments 1 & 2 (Customer Segmentation, Sales Forecasting)")
    print("")
    
    # Step 3: Test current user still works
    print("3️⃣ Current user (kushit@techdwarfs.com) should still see:")
    print("   - Experiments 1 & 2 (Customer Segmentation, Sales Forecasting)")
    print("   - Should NOT see experiments 3 & 4 (Fraud Detection, Recommendation Engine)")
    print("")
    
    print("🎯 This will prove that the policy-based access control is working correctly!")

if __name__ == "__main__":
    test_new_user_flow()

