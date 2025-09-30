#!/usr/bin/env python3
"""
Test script to verify the policy and MLflow integration works
"""
import requests
import json

def test_policy_and_mlflow():
    """Test the complete flow"""
    
    # Your access token
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkhTMjNiN0RvN1RjYVUxUm9MSHdwSXEyNFZZZyIsImtpZCI6IkhTMjNiN0RvN1RjYVUxUm9MSHdwSXEyNFZZZyJ9.eyJhdWQiOiJhcGk6Ly8xNjE3ZjgzYi02YzlmLTQ3NGItYjVlNS1lZjUxNDA4YjU2ZTYiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC81Zjg5MmQ3Yi02Mjk0LTRmNzUtYWEwOS0yMGZiNDUwYjliZjIvIiwiaWF0IjoxNzU4ODgxMzc3LCJuYmYiOjE3NTg4ODEzNzcsImV4cCI6MTc1ODg4NTM5MiwiYWNyIjoiMSIsImFpbyI6IkFaUUFhLzhaQUFBQWxRT004WDBxaUhYU2xNWERURmhzdFZQMWh6MGJlcmFZZ1lmNEhzOUlWZGZpZG1sUXFZQVU3a3hZT2pkODNwME1Kc254S09lamRxd3BGY0YydVVRYmEyQW00c0J3THhKekpjN1BtRkhnY2FOVUlDMWR6Z2hFV1M0UVgxL2VKUGhVMWlUcEJWZUllYXdyYmNiL2RVNkgvVzRQTHI1TFdkQkcxTXRFNGJLcnNXRnZRY0lON3lWeklwMnVRMWVETTJzaCIsImFtciI6WyJwd2QiLCJtZmEiXSwiYXBwaWQiOiIxNjE3ZjgzYi02YzlmLTQ3NGItYjVlNS1lZjUxNDA4YjU2ZTYiLCJhcHBpZGFjciI6IjEiLCJmYW1pbHlfbmFtZSI6IlR1bHNpeWFuIiwiZ2l2ZW5fbmFtZSI6Ikt1c2hpIiwiaXBhZGRyIjoiMTI1Ljk5LjI1MS43MCIsIm5hbWUiOiJLdXNoaSBUdWxzaXlhbiIsIm9pZCI6IjU2YzU4YTZhLTc1YzktNDY5Yy1iZTVlLWU0Y2E4MWM5NTU2MSIsInJoIjoiMS5BU3NBZXkySlg1UmlkVS1xQ1NEN1JRdWI4anY0RnhhZmJFdEh0ZVh2VVVDTFZ1Ym9BSzRyQUEuIiwic2NwIjoidXNlcl9pbXBlcnNvbmF0aW9uIiwic2lkIjoiMDA4Y2I3ODktYmI5Yi03MjM3LTcxZWQtOGI0ZjBmYjQ4NjRiIiwic3ViIjoiSjB0UWh2NndGUmI0LTZFV0EwR0FadXl1clJKdEpnT3kzZjlZMU9GZ2EwMCIsInRpZCI6IjVmODkyZDdiLTYyOTQtNGY3NS1hYTA5LTIwZmI0NTBiOWJmMiIsInVuaXF1ZV9uYW1lIjoiS3VzaGlUQHRlY2hkd2FyZnMuY29tIiwidXBuIjoiS3VzaGlUQHRlY2hkd2FyZnMuY29tIiwidXRpIjoicWh2U2pTZ0Iza3U0bkdSaE9GYjNBQSIsInZlciI6IjEuMCIsInhtc19mdGQiOiJXbW5kTDVOVmJ0ZEV6RVNXWVREanR3LU55MlpLaGpZalVUWnlXRzBodFVvQmFtRndZVzVsWVhOMExXUnpiWE0ifQ.PRggS6zPYpT-TSrGnJARMWdJ8ewuqX0lPzOK67WH6bI3oP4Vp3Ax06ZZMOjL6DNhjoBtxJpxDMVmE-o6UVr01kCFrMJOF2r-uKEU5bUlc8CNXbBtBVf39W0H-kF-ks4miPtzl3veUAzB0BIrrknLKFOdUWdqnVN-YfsNXNcSfo8Vw4AaR2lt_nywxFBflcPLf2-vVWw3UYLrKW0ut3K0t_kkZUKHudNzwj2gLo5BsxJOsN2QhszqnYcCJKA3QAM5acMO_UM9dFSvi-hWqEhWZo7XzmQl52lOylfg5P8cEUVZpseoOaJkPPdAWN7JUTZKqLgFg1Tq7EiKgQa-fl6-0g"
    
    print("🧪 Testing complete OAuth flow with MLflow integration...")
    
    # Test 1: OAuth/me endpoint
    print("\n1️⃣ Testing /oauth/me endpoint...")
    try:
        response = requests.get("http://localhost:8081/oauth/me", 
                              headers={"Authorization": f"Bearer {token}"})
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"User: {data.get('user', {}).get('email', 'N/A')}")
        print(f"Experiments: {data.get('experiments', [])}")
        
        if data.get('experiments'):
            print("✅ Policy is working - experiments found!")
        else:
            print("❌ Policy not working - no experiments found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Direct MLflow access
    print("\n2️⃣ Testing direct MLflow access...")
    try:
        response = requests.get("http://localhost:5000/api/2.0/mlflow/experiments/search?max_results=10")
        print(f"Status: {response.status_code}")
        data = response.json()
        experiments = data.get('experiments', [])
        print(f"Found {len(experiments)} experiments in MLflow:")
        for exp in experiments:
            print(f"  - ID: {exp.get('experiment_id')}, Name: {exp.get('name')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Policy file content
    print("\n3️⃣ Testing policy file...")
    try:
        response = requests.get("http://localhost:8081/oauth/me", 
                              headers={"Authorization": f"Bearer {token}"})
        data = response.json()
        user_email = data.get('user', {}).get('email', '')
        
        # Expected experiments for kushit@techdwarfs.com
        expected_experiments = ["1", "2"]
        print(f"User email: {user_email}")
        print(f"Expected experiments: {expected_experiments}")
        print(f"Actual experiments: {data.get('experiments', [])}")
        
        if data.get('experiments') == expected_experiments:
            print("✅ Policy file is working correctly!")
        else:
            print("❌ Policy file not working - experiments don't match")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_policy_and_mlflow()

