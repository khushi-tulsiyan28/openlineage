#!/usr/bin/env python3
"""
Mock Feast Feature Store Service
"""
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Feast Feature Store", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "feast"}

@app.get("/get-online-features")
async def get_online_features():
    return {"features": [], "message": "Feast mock endpoint"}

@app.get("/{path:path}")
async def catch_all(path: str):
    return {"message": f"Feast endpoint: {path}", "status": "mock"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6566)
