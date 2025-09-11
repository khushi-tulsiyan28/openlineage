import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
from jwt import PyJWKClient
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EntraIDConfig(BaseModel):
    tenant_id: str
    client_id: str
    client_secret: str
    authority: str
    scopes: list
    audience: str

class UserInfo(BaseModel):
    user_id: str
    email: str
    name: str
    groups: list
    roles: list

class ExperimentAccess(BaseModel):
    experiment_id: str
    user_id: str
    permissions: list
    created_at: datetime

app = FastAPI(title="MLOps API Gateway", version="1.0.0")

security = HTTPBearer()

entra_config = None
jwks_client = None
user_sessions = {}
experiment_permissions = {}

def load_config():
    global entra_config, jwks_client
    
    config_path = os.getenv("API_GATEWAY_CONFIG_PATH", "/app/config/api-gateway-config.yaml")
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        entra_config = EntraIDConfig(
            tenant_id=os.getenv("ENTRA_TENANT_ID", config.get("entra_id", {}).get("tenant_id", "")),
            client_id=os.getenv("ENTRA_CLIENT_ID", config.get("entra_id", {}).get("client_id", "")),
            client_secret=os.getenv("ENTRA_CLIENT_SECRET", config.get("entra_id", {}).get("client_secret", "")),
            authority=f"https://login.microsoftonline.com/{os.getenv('ENTRA_TENANT_ID', config.get('entra_id', {}).get('tenant_id', ''))}",
            scopes=config.get("entra_id", {}).get("scopes", ["openid", "profile", "email"]),
            audience=config.get("entra_id", {}).get("audience", "")
        )
        
        jwks_uri = f"https://login.microsoftonline.com/{entra_config.tenant_id}/discovery/v2.0/keys"
        jwks_client = PyJWKClient(jwks_uri)
        
        logger.info("Entra ID configuration loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

async def verify_entra_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInfo:
    try:
        token = credentials.credentials
        
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=entra_config.audience,
            issuer=f"https://login.microsoftonline.com/{entra_config.tenant_id}/v2.0"
        )
        
        user_info = UserInfo(
            user_id=payload.get("oid", payload.get("sub", "")),
            email=payload.get("email", payload.get("preferred_username", "")),
            name=payload.get("name", ""),
            groups=payload.get("groups", []),
            roles=payload.get("roles", [])
        )
        
        user_sessions[user_info.user_id] = {
            "user_info": user_info,
            "token": token,
            "expires_at": datetime.utcnow() + timedelta(hours=1)
        }
        
        return user_info
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")

async def check_experiment_permission(experiment_id: str, user: UserInfo, required_permission: str = "read") -> bool:
    user_key = f"{user.user_id}:{experiment_id}"
    
    if user_key in experiment_permissions:
        permissions = experiment_permissions[user_key]["permissions"]
        return required_permission in permissions or "admin" in permissions
    
    if "mlflow:admin" in user.roles:
        return True
    
    if "mlflow:write" in user.roles and required_permission in ["read", "write"]:
        return True
    
    if "mlflow:read" in user.roles and required_permission == "read":
        return True
    
    return False

async def forward_to_mlflow(request: Request, user: UserInfo, path: str):
    mlflow_url = os.getenv("MLFLOW_URL", "http://mlflow:5000")
    
    headers = {
        "Authorization": f"Bearer {user_sessions[user.user_id]['token']}",
        "X-User-ID": user.user_id,
        "X-User-Email": user.email,
        "X-User-Name": user.name,
        "X-User-Groups": ",".join(user.groups),
        "X-User-Roles": ",".join(user.roles)
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=f"{mlflow_url}/{path}",
                headers=headers,
                content=await request.body(),
                params=request.query_params,
                timeout=30.0
            )
            
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        except httpx.RequestError as e:
            logger.error(f"MLflow request failed: {e}")
            raise HTTPException(status_code=502, detail="MLflow service unavailable")

@app.on_event("startup")
async def startup_event():
    load_config()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/health") or request.url.path.startswith("/docs"):
        return await call_next(request)
    
    if request.url.path.startswith("/oauth"):
        return await call_next(request)
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization header required"}
        )
    
    try:
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=auth_header.split(" ")[1]
        )
        user = await verify_entra_token(credentials)
        request.state.user = user
    except HTTPException:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or expired token"}
        )
    
    response = await call_next(request)
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/oauth/authorize")
async def oauth_authorize():
    auth_url = f"{entra_config.authority}/oauth2/v2.0/authorize"
    params = {
        "client_id": entra_config.client_id,
        "response_type": "code",
        "redirect_uri": os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8081/oauth/callback"),
        "scope": " ".join(entra_config.scopes),
        "response_mode": "query"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return {"authorization_url": f"{auth_url}?{query_string}"}

@app.post("/oauth/token")
async def exchange_token(code: str, redirect_uri: str):
    token_url = f"{entra_config.authority}/oauth2/v2.0/token"
    
    data = {
        "client_id": entra_config.client_id,
        "client_secret": entra_config.client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Token exchange failed: {e}")
            raise HTTPException(status_code=400, detail="Token exchange failed")

@app.get("/mlflow/experiments")
async def list_experiments(user: UserInfo = Depends(verify_entra_token)):
    return await forward_to_mlflow(request, user, "api/2.0/mlflow/experiments/list")

@app.post("/mlflow/experiments")
async def create_experiment(request: Request, user: UserInfo = Depends(verify_entra_token)):
    return await forward_to_mlflow(request, user, "api/2.0/mlflow/experiments/create")

@app.get("/mlflow/experiments/{experiment_id}")
async def get_experiment(experiment_id: str, user: UserInfo = Depends(verify_entra_token)):
    if not await check_experiment_permission(experiment_id, user, "read"):
        raise HTTPException(status_code=403, detail="Access denied to experiment")
    
    return await forward_to_mlflow(request, user, f"api/2.0/mlflow/experiments/get?experiment_id={experiment_id}")

@app.post("/mlflow/experiments/{experiment_id}/runs")
async def create_run(experiment_id: str, request: Request, user: UserInfo = Depends(verify_entra_token)):
    if not await check_experiment_permission(experiment_id, user, "write"):
        raise HTTPException(status_code=403, detail="Access denied to experiment")
    
    return await forward_to_mlflow(request, user, f"api/2.0/mlflow/runs/create")

@app.get("/mlflow/experiments/{experiment_id}/runs")
async def list_runs(experiment_id: str, user: UserInfo = Depends(verify_entra_token)):
    if not await check_experiment_permission(experiment_id, user, "read"):
        raise HTTPException(status_code=403, detail="Access denied to experiment")
    
    return await forward_to_mlflow(request, user, f"api/2.0/mlflow/runs/search")

@app.post("/mlflow/models/register")
async def register_model(request: Request, user: UserInfo = Depends(verify_entra_token)):
    if "mlflow:write" not in user.roles and "mlflow:admin" not in user.roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions to register models")
    
    return await forward_to_mlflow(request, user, "api/2.0/mlflow/model-versions/create")

@app.get("/mlflow/models")
async def list_models(user: UserInfo = Depends(verify_entra_token)):
    return await forward_to_mlflow(request, user, "api/2.0/mlflow/registered-models/search")

@app.get("/user/profile")
async def get_user_profile(user: UserInfo = Depends(verify_entra_token)):
    return {
        "user_id": user.user_id,
        "email": user.email,
        "name": user.name,
        "groups": user.groups,
        "roles": user.roles,
        "permissions": {
            "mlflow_read": "mlflow:read" in user.roles or "mlflow:admin" in user.roles,
            "mlflow_write": "mlflow:write" in user.roles or "mlflow:admin" in user.roles,
            "mlflow_admin": "mlflow:admin" in user.roles
        }
    }

@app.post("/admin/experiments/{experiment_id}/permissions")
async def set_experiment_permissions(
    experiment_id: str, 
    user_id: str, 
    permissions: list, 
    current_user: UserInfo = Depends(verify_entra_token)
):
    if "mlflow:admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user_key = f"{user_id}:{experiment_id}"
    experiment_permissions[user_key] = ExperimentAccess(
        experiment_id=experiment_id,
        user_id=user_id,
        permissions=permissions,
        created_at=datetime.utcnow()
    )
    
    return {"message": "Permissions updated successfully"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("API_GATEWAY_PORT", 8080)),
        reload=False
    )
