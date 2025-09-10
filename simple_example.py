#!/usr/bin/env python3
"""
Simple MLOps Example
This demonstrates basic MLflow functionality with our Phase 1 platform.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

def create_sample_data():
    """Create sample data for demonstration."""
    np.random.seed(42)
    n_samples = 1000
    
    # Generate synthetic data
    data = {
        'age': np.random.randint(18, 80, n_samples),
        'income': np.random.normal(50000, 20000, n_samples),
        'credit_score': np.random.randint(300, 850, n_samples),
        'loan_amount': np.random.normal(25000, 10000, n_samples),
        'employment_years': np.random.randint(0, 40, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Create target variable (loan approval)
    # Simple rule: approve if credit_score > 650 and income > 40000
    df['loan_approved'] = ((df['credit_score'] > 650) & (df['income'] > 40000)).astype(int)
    
    return df

def train_model(X_train, y_train, X_test, y_test):
    """Train a Random Forest model and log to MLflow."""
    
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")
    
    # Create experiment
    experiment_name = "Loan Approval Prediction"
    try:
        experiment_id = mlflow.create_experiment(experiment_name)
        print(f"Created new experiment: {experiment_name}")
    except:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id
        print(f"Using existing experiment: {experiment_name}")
    
    with mlflow.start_run(experiment_id=experiment_id) as run:
        print(f"Started MLflow run: {run.info.run_id}")
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Log parameters
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("random_state", 42)
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        # Log additional info
        mlflow.set_tag("model_type", "RandomForest")
        mlflow.set_tag("task", "classification")
        mlflow.set_tag("dataset", "loan_approval")
        
        print(f"Model accuracy: {accuracy:.4f}")
        print(f"Run ID: {run.info.run_id}")
        
        return model, run.info.run_id

def main():
    """Main function to run the example."""
    print("=== Simple MLOps Example ===")
    print("Creating sample data...")
    
    # Create sample data
    df = create_sample_data()
    print(f"Created dataset with {len(df)} samples")
    print(f"Features: {list(df.columns[:-1])}")
    print(f"Target: {df.columns[-1]}")
    
    # Prepare features and target
    X = df.drop('loan_approved', axis=1)
    y = df['loan_approved']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train model and log to MLflow
    print("\nTraining model and logging to MLflow...")
    model, run_id = train_model(X_train, y_train, X_test, y_test)
    
    # Test model prediction
    print("\nTesting model prediction...")
    sample_prediction = model.predict(X_test.head(1))
    print(f"Sample prediction: {sample_prediction[0]}")
    
    print(f"\n=== Example Complete ===")
    print(f"MLflow UI: http://localhost:5000")
    print(f"Run ID: {run_id}")
    print("Check the MLflow UI to see the logged experiment!")

if __name__ == "__main__":
    main()
