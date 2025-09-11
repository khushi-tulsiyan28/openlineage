import os
import json
import asyncio
import webbrowser
from urllib.parse import urlparse, parse_qs
import httpx
from fastapi import FastAPI, Request
import uvicorn

class EntraAuthClient:
    def __init__(self, tenant_id: str, client_id: str, redirect_uri: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.access_token = None
        self.user_info = None

    def get_authorization_url(self, scopes: list = None):
        if scopes is None:
            scopes = ["openid", "profile", "email"]
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "response_mode": "query"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.authority}/oauth2/v2.0/authorize?{query_string}"

    async def exchange_code_for_token(self, code: str, client_secret: str):
        token_url = f"{self.authority}/oauth2/v2.0/token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data["access_token"]
            return token_data

    async def get_user_info(self):
        if not self.access_token:
            raise ValueError("No access token available")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.microsoft.com/v1.0/me",
                headers=headers
            )
            response.raise_for_status()
            self.user_info = response.json()
            return self.user_info

    async def call_mlflow_api(self, endpoint: str, method: str = "GET", data: dict = None):
        if not self.access_token:
            raise ValueError("No access token available")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        api_gateway_url = "http://localhost:8081"
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(f"{api_gateway_url}{endpoint}", headers=headers)
            elif method == "POST":
                response = await client.post(f"{api_gateway_url}{endpoint}", headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()

async def main():
    tenant_id = os.getenv("ENTRA_TENANT_ID", "your-tenant-id")
    client_id = os.getenv("ENTRA_CLIENT_ID", "your-client-id")
    client_secret = os.getenv("ENTRA_CLIENT_SECRET", "your-client-secret")
    redirect_uri = "http://localhost:8080/callback"
    
    auth_client = EntraAuthClient(tenant_id, client_id, redirect_uri)
    
    print("=== Entra ID Authentication Example ===")
    print(f"Tenant ID: {tenant_id}")
    print(f"Client ID: {client_id}")
    print(f"Redirect URI: {redirect_uri}")
    print()
    
    auth_url = auth_client.get_authorization_url()
    print(f"Authorization URL: {auth_url}")
    print()
    print("Please open this URL in your browser to authenticate...")
    
    webbrowser.open(auth_url)
    
    print("Waiting for authorization code...")
    print("After authentication, you'll be redirected to a localhost URL.")
    print("Copy the 'code' parameter from the URL and paste it here.")
    
    code = input("Enter authorization code: ").strip()
    
    try:
        print("\nExchanging code for token...")
        token_data = await auth_client.exchange_code_for_token(code, client_secret)
        print("✅ Token obtained successfully!")
        print(f"Token type: {token_data.get('token_type')}")
        print(f"Expires in: {token_data.get('expires_in')} seconds")
        
        print("\nGetting user information...")
        user_info = await auth_client.get_user_info()
        print("✅ User information retrieved!")
        print(f"Name: {user_info.get('displayName')}")
        print(f"Email: {user_info.get('mail') or user_info.get('userPrincipalName')}")
        print(f"ID: {user_info.get('id')}")
        
        print("\nTesting MLflow API access...")
        
        try:
            profile = await auth_client.call_mlflow_api("/user/profile")
            print("✅ User profile retrieved from API Gateway!")
            print(f"User ID: {profile.get('user_id')}")
            print(f"Email: {profile.get('email')}")
            print(f"Roles: {profile.get('roles')}")
            print(f"Permissions: {profile.get('permissions')}")
        except Exception as e:
            print(f"❌ Failed to get user profile: {e}")
        
        try:
            experiments = await auth_client.call_mlflow_api("/mlflow/experiments")
            print("✅ MLflow experiments retrieved!")
            print(f"Number of experiments: {len(experiments.get('experiments', []))}")
        except Exception as e:
            print(f"❌ Failed to get experiments: {e}")
        
        print("\n=== Authentication Flow Complete ===")
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
