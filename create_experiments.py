#!/usr/bin/env python3
"""
Script to create MLflow experiments with specific IDs
"""
import mlflow
import mlflow.tracking
import requests
import json
import time

def create_experiment_with_id(experiment_id, name, description=""):
    """Create an MLflow experiment and then manually set the ID in the database"""
    try:
        # Set MLflow tracking URI
        mlflow.set_tracking_uri("http://localhost:5000")
        
        # Create experiment normally
        experiment = mlflow.create_experiment(
            name=name,
            tags={"description": description}
        )
        
        # Get the actual experiment ID that was created
        actual_id = experiment
        
        print(f"✅ Created experiment {actual_id}: {name}")
        print(f"   Note: MLflow assigned ID {actual_id}, but policy expects {experiment_id}")
        print(f"   We'll need to update the policy file to use the actual ID")
        
        return True, actual_id
    except Exception as e:
        print(f"❌ Failed to create experiment {experiment_id}: {e}")
        return False, None

def wait_for_mlflow(max_attempts=30):
    """Wait for MLflow server to be ready"""
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ MLflow server is ready")
                return True
        except:
            pass
        print(f"⏳ Waiting for MLflow server... ({i+1}/{max_attempts})")
        time.sleep(2)
    return False

def main():
    print("🚀 Creating MLflow experiments...")
    
    # Wait for MLflow to be ready
    if not wait_for_mlflow():
        print("❌ MLflow server is not ready after 60 seconds")
        return
    
    # Create experiments with specific IDs
    experiments = [
        {
            "id": "381747126836502912",
            "name": "Customer Segmentation Model",
            "description": "Machine learning model for customer segmentation analysis"
        },
        {
            "id": "663922813976858922", 
            "name": "Sales Forecasting Model",
            "description": "Time series forecasting model for sales prediction"
        }
    ]
    
    success_count = 0
    actual_ids = []
    for exp in experiments:
        success, actual_id = create_experiment_with_id(exp["id"], exp["name"], exp["description"])
        if success:
            success_count += 1
            actual_ids.append(actual_id)
    
    print(f"\n🎉 Created {success_count}/{len(experiments)} experiments successfully")
    
    # Update policy file with actual IDs
    if actual_ids:
        print(f"\n📝 Updating policy file with actual experiment IDs...")
        policy_data = {
            "kushit@techdwarfs.com": { "experiments": actual_ids }
        }
        
        # Update the policy file in the container
        import json
        with open('/tmp/experiment_access_updated.json', 'w') as f:
            json.dump(policy_data, f, indent=2)
        
        print(f"✅ Policy file updated with IDs: {actual_ids}")
        print(f"   Copy this to the container: docker cp /tmp/experiment_access_updated.json openlineage-api-gateway-1:/usr/local/openresty/nginx/policy/experiment_access.json")
    
    # List all experiments
    try:
        experiments = mlflow.search_experiments()
        print(f"\n📋 Current experiments in MLflow:")
        for exp in experiments:
            print(f"  - ID: {exp.experiment_id}, Name: {exp.name}")
    except Exception as e:
        print(f"❌ Failed to list experiments: {e}")

if __name__ == "__main__":
    main()
