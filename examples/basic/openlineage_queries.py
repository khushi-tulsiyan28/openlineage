"""
OpenLineage Query Examples
This module provides examples of querying Marquez for lineage information.
"""

import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class MarquezQueryClient:
    """Client for querying Marquez OpenLineage backend."""
    
    def __init__(self, marquez_url: str = "http://localhost:5000"):
        """Initialize the client with Marquez URL."""
        self.base_url = marquez_url
        self.api_url = f"{marquez_url}/api/v1"
        
    def get_lineage_for_model(self, model_name: str, model_version: str = None) -> Dict[str, Any]:
        """Get complete lineage for a specific model."""
        url = f"{self.api_url}/lineage"
        params = {
            "nodeId": f"modelcatalogue:model_{model_name}",
            "depth": 10,
            "direction": "upstream"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
        
    def get_impact_analysis(self, dataset_name: str, dataset_namespace: str = "raw_data") -> Dict[str, Any]:
        """Get downstream impact analysis for a dataset."""
        url = f"{self.api_url}/lineage"
        params = {
            "nodeId": f"{dataset_namespace}:{dataset_name}",
            "depth": 10,
            "direction": "downstream"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
        
    def get_feature_lineage(self, feature_view_name: str) -> Dict[str, Any]:
        """Get lineage for a specific feature view."""
        url = f"{self.api_url}/lineage"
        params = {
            "nodeId": f"feast:feature_view_{feature_view_name}",
            "depth": 5,
            "direction": "both"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
        
    def get_experiment_lineage(self, experiment_id: str) -> Dict[str, Any]:
        """Get lineage for an MLflow experiment."""
        url = f"{self.api_url}/lineage"
        params = {
            "nodeId": f"mlflow:experiment_{experiment_id}",
            "depth": 5,
            "direction": "both"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
        
    def get_job_runs(self, job_name: str, namespace: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent runs for a specific job."""
        url = f"{self.api_url}/namespaces/{namespace}/jobs/{job_name}/runs"
        params = {"limit": limit}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("runs", [])
        
    def get_dataset_versions(self, dataset_name: str, namespace: str) -> List[Dict[str, Any]]:
        """Get versions for a specific dataset."""
        url = f"{self.api_url}/namespaces/{namespace}/datasets/{dataset_name}/versions"
        
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("versions", [])
        
    def search_datasets(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for datasets by name or description."""
        url = f"{self.api_url}/search/datasets"
        params = {"q": query, "limit": limit}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
        
    def get_namespace_summary(self, namespace: str) -> Dict[str, Any]:
        """Get summary information for a namespace."""
        url = f"{self.api_url}/namespaces/{namespace}"
        
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

def example_queries():
    """Example queries demonstrating Marquez capabilities."""
    
    client = MarquezQueryClient()
    
    print("=== OpenLineage Query Examples ===\n")
    
    # 1. Get lineage for a specific model
    print("1. Model Lineage Query")
    print("-" * 30)
    try:
        model_lineage = client.get_lineage_for_model("loan_approval_model", "v1.0")
        print(f"Model lineage: {json.dumps(model_lineage, indent=2)}")
    except Exception as e:
        print(f"Error querying model lineage: {e}")
    print()
    
    # 2. Impact analysis for a dataset
    print("2. Dataset Impact Analysis")
    print("-" * 30)
    try:
        impact = client.get_impact_analysis("customer_data", "raw_data")
        print(f"Impact analysis: {json.dumps(impact, indent=2)}")
    except Exception as e:
        print(f"Error querying impact analysis: {e}")
    print()
    
    # 3. Feature lineage
    print("3. Feature Lineage Query")
    print("-" * 30)
    try:
        feature_lineage = client.get_feature_lineage("customer_features")
        print(f"Feature lineage: {json.dumps(feature_lineage, indent=2)}")
    except Exception as e:
        print(f"Error querying feature lineage: {e}")
    print()
    
    # 4. Search for datasets
    print("4. Dataset Search")
    print("-" * 30)
    try:
        search_results = client.search_datasets("customer", limit=5)
        print(f"Search results: {json.dumps(search_results, indent=2)}")
    except Exception as e:
        print(f"Error searching datasets: {e}")
    print()
    
    # 5. Get namespace summary
    print("5. Namespace Summary")
    print("-" * 30)
    try:
        namespace_summary = client.get_namespace_summary("mlflow")
        print(f"Namespace summary: {json.dumps(namespace_summary, indent=2)}")
    except Exception as e:
        print(f"Error querying namespace: {e}")
    print()

def advanced_lineage_queries():
    """Advanced lineage queries for complex scenarios."""
    
    client = MarquezQueryClient()
    
    print("=== Advanced Lineage Queries ===\n")
    
    # 1. Find all models that use a specific feature
    print("1. Models Using Specific Feature")
    print("-" * 40)
    try:
        # Get lineage for the feature
        feature_lineage = client.get_feature_lineage("customer_features")
        
        # Extract downstream models
        models = []
        if "graph" in feature_lineage:
            for node in feature_lineage["graph"].get("nodes", []):
                if "modelcatalogue" in node.get("id", ""):
                    models.append(node)
        
        print(f"Models using customer_features: {json.dumps(models, indent=2)}")
    except Exception as e:
        print(f"Error finding models: {e}")
    print()
    
    # 2. Find all datasets that feed into a model
    print("2. Datasets Feeding into Model")
    print("-" * 40)
    try:
        model_lineage = client.get_lineage_for_model("loan_approval_model")
        
        # Extract upstream datasets
        datasets = []
        if "graph" in model_lineage:
            for node in model_lineage["graph"].get("nodes", []):
                if "dataset" in node.get("type", ""):
                    datasets.append(node)
        
        print(f"Datasets feeding into model: {json.dumps(datasets, indent=2)}")
    except Exception as e:
        print(f"Error finding datasets: {e}")
    print()
    
    # 3. Get recent job runs with status
    print("3. Recent Job Runs")
    print("-" * 40)
    try:
        runs = client.get_job_runs("model_training_loan_approval_model", "mlflow", limit=10)
        
        # Filter for recent runs
        recent_runs = []
        for run in runs:
            if run.get("state") in ["COMPLETED", "FAILED", "RUNNING"]:
                recent_runs.append({
                    "runId": run.get("id"),
                    "state": run.get("state"),
                    "startTime": run.get("startedAt"),
                    "endTime": run.get("endedAt")
                })
        
        print(f"Recent job runs: {json.dumps(recent_runs, indent=2)}")
    except Exception as e:
        print(f"Error getting job runs: {e}")
    print()

def lineage_impact_analysis():
    """Comprehensive lineage impact analysis."""
    
    client = MarquezQueryClient()
    
    print("=== Lineage Impact Analysis ===\n")
    
    # 1. What happens if customer_data changes?
    print("1. Impact of customer_data Changes")
    print("-" * 40)
    try:
        impact = client.get_impact_analysis("customer_data", "raw_data")
        
        # Analyze impact
        affected_components = {
            "feature_views": [],
            "models": [],
            "experiments": []
        }
        
        if "graph" in impact:
            for node in impact["graph"].get("nodes", []):
                node_id = node.get("id", "")
                if "feast" in node_id:
                    affected_components["feature_views"].append(node_id)
                elif "modelcatalogue" in node_id:
                    affected_components["models"].append(node_id)
                elif "mlflow" in node_id:
                    affected_components["experiments"].append(node_id)
        
        print(f"Impact analysis results: {json.dumps(affected_components, indent=2)}")
    except Exception as e:
        print(f"Error in impact analysis: {e}")
    print()
    
    # 2. Data freshness analysis
    print("2. Data Freshness Analysis")
    print("-" * 40)
    try:
        # Get recent runs for data ingestion jobs
        ingestion_runs = client.get_job_runs("feature_ingestion_customer_features", "feast", limit=5)
        
        freshness_analysis = []
        for run in ingestion_runs:
            if run.get("state") == "COMPLETED":
                start_time = run.get("startedAt")
                end_time = run.get("endedAt")
                if start_time and end_time:
                    duration = datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)
                    freshness_analysis.append({
                        "runId": run.get("id"),
                        "duration": str(duration),
                        "endTime": end_time,
                        "status": "fresh" if duration < timedelta(hours=1) else "stale"
                    })
        
        print(f"Data freshness analysis: {json.dumps(freshness_analysis, indent=2)}")
    except Exception as e:
        print(f"Error in freshness analysis: {e}")
    print()

def compliance_queries():
    """Queries for compliance and governance."""
    
    client = MarquezQueryClient()
    
    print("=== Compliance and Governance Queries ===\n")
    
    # 1. Audit trail for model changes
    print("1. Model Change Audit Trail")
    print("-" * 40)
    try:
        # Get all runs for model registration
        registration_runs = client.get_job_runs("model_registration_loan_approval_model", "modelcatalogue", limit=20)
        
        audit_trail = []
        for run in registration_runs:
            audit_trail.append({
                "runId": run.get("id"),
                "state": run.get("state"),
                "startTime": run.get("startedAt"),
                "endTime": run.get("endedAt"),
                "facets": run.get("facets", {})
            })
        
        print(f"Model change audit trail: {json.dumps(audit_trail, indent=2)}")
    except Exception as e:
        print(f"Error getting audit trail: {e}")
    print()
    
    # 2. Data lineage for compliance
    print("2. Data Lineage for Compliance")
    print("-" * 40)
    try:
        # Get complete lineage for sensitive data
        sensitive_data_lineage = client.get_lineage_for_model("loan_approval_model")
        
        # Extract compliance-relevant information
        compliance_info = {
            "data_sources": [],
            "transformations": [],
            "models": [],
            "deployments": []
        }
        
        if "graph" in sensitive_data_lineage:
            for node in sensitive_data_lineage["graph"].get("nodes", []):
                node_type = node.get("type", "")
                node_id = node.get("id", "")
                
                if "dataset" in node_type:
                    compliance_info["data_sources"].append({
                        "id": node_id,
                        "name": node.get("name"),
                        "namespace": node.get("namespace")
                    })
                elif "job" in node_type:
                    compliance_info["transformations"].append({
                        "id": node_id,
                        "name": node.get("name"),
                        "namespace": node.get("namespace")
                    })
        
        print(f"Compliance information: {json.dumps(compliance_info, indent=2)}")
    except Exception as e:
        print(f"Error getting compliance info: {e}")
    print()

if __name__ == "__main__":
    # Run all example queries
    example_queries()
    advanced_lineage_queries()
    lineage_impact_analysis()
    compliance_queries()
    
    print("=== Query Examples Complete ===")
    print("These examples demonstrate how to query Marquez for:")
    print("- Model lineage and dependencies")
    print("- Impact analysis for data changes")
    print("- Feature lineage and usage")
    print("- Job run history and status")
    print("- Compliance and audit information")
    print("\nTo run these queries, ensure Marquez is running on localhost:5000")
    print("and that the MLOps workflow has been executed to populate the data.")
