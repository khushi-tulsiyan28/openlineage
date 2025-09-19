#!/usr/bin/env python3
"""
Mock MLflow Service with Multiple Experiments
"""
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

app = FastAPI(title="Mock MLflow Service", version="1.0.0")

# Mock experiments data (10 experiments total)
MOCK_EXPERIMENTS = {
    "experiments": [
        {
            "experiment_id": "0",
            "name": "Default Experiment",
            "artifact_location": "s3://mlflow-artifacts/0",
            "lifecycle_stage": "active",
            "tags": {"team": "ml-engineering"}
        },
        {
            "experiment_id": "1", 
            "name": "Customer Segmentation",
            "artifact_location": "s3://mlflow-artifacts/1",
            "lifecycle_stage": "active",
            "tags": {"team": "data-science"}
        },
        {
            "experiment_id": "2",
            "name": "Fraud Detection",
            "artifact_location": "s3://mlflow-artifacts/2", 
            "lifecycle_stage": "active",
            "tags": {"team": "security"}
        },
        {
            "experiment_id": "3",
            "name": "Recommendation Engine",
            "artifact_location": "s3://mlflow-artifacts/3",
            "lifecycle_stage": "active", 
            "tags": {"team": "ml-engineering"}
        },
        {
            "experiment_id": "4",
            "name": "Price Prediction",
            "artifact_location": "s3://mlflow-artifacts/4",
            "lifecycle_stage": "active",
            "tags": {"team": "data-science"}
        },
        {
            "experiment_id": "5",
            "name": "Image Classification",
            "artifact_location": "s3://mlflow-artifacts/5",
            "lifecycle_stage": "active",
            "tags": {"team": "computer-vision"}
        },
        {
            "experiment_id": "6",
            "name": "NLP Sentiment Analysis",
            "artifact_location": "s3://mlflow-artifacts/6",
            "lifecycle_stage": "active",
            "tags": {"team": "nlp"}
        },
        {
            "experiment_id": "7",
            "name": "Time Series Forecasting",
            "artifact_location": "s3://mlflow-artifacts/7",
            "lifecycle_stage": "active",
            "tags": {"team": "data-science"}
        },
        {
            "experiment_id": "8",
            "name": "A/B Testing Framework",
            "artifact_location": "s3://mlflow-artifacts/8",
            "lifecycle_stage": "active",
            "tags": {"team": "ml-engineering"}
        },
        {
            "experiment_id": "9",
            "name": "Model Monitoring",
            "artifact_location": "s3://mlflow-artifacts/9",
            "lifecycle_stage": "active",
            "tags": {"team": "ml-ops"}
        }
    ]
}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mock-mlflow"}

@app.get("/experiments")
async def get_experiments():
    """Return all experiments (will be filtered by nginx gateway)"""
    return MOCK_EXPERIMENTS

@app.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: str):
    """Return specific experiment details"""
    for exp in MOCK_EXPERIMENTS["experiments"]:
        if exp["experiment_id"] == experiment_id:
            return exp
    
    return JSONResponse(
        status_code=404,
        content={"error": "experiment_not_found", "message": f"Experiment {experiment_id} not found"}
    )

@app.get("/runs")
async def get_runs():
    """Return mock runs data"""
    return {
        "runs": [
            {
                "run_id": "run-001",
                "experiment_id": "0",
                "status": "FINISHED",
                "start_time": "2025-09-19T10:00:00Z"
            },
            {
                "run_id": "run-002", 
                "experiment_id": "1",
                "status": "RUNNING",
                "start_time": "2025-09-19T11:00:00Z"
            },
            {
                "run_id": "run-003",
                "experiment_id": "2", 
                "status": "FINISHED",
                "start_time": "2025-09-19T12:00:00Z"
            }
        ]
    }

@app.get("/")
async def mlflow_ui():
    """Mock MLflow UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>MLflow UI</title></head>
    <body>
        <h1>MLflow UI</h1>
        <p>This is a mock MLflow UI. In a real implementation, this would show the filtered experiments.</p>
        <p>Access the API Gateway at <a href="http://localhost:8081/mlflow/experiments">http://localhost:8081/mlflow/experiments</a></p>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
