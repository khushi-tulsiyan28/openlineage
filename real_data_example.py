#!/usr/bin/env python3
"""
Real Data MLOps Example
This demonstrates MLflow with a real-world dataset (Iris classification).
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.datasets import load_iris, load_wine, load_breast_cancer
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

def load_dataset(dataset_name="iris"):
    """Load a real dataset."""
    if dataset_name == "iris":
        data = load_iris()
        description = "Iris flower classification dataset"
    elif dataset_name == "wine":
        data = load_wine()
        description = "Wine quality classification dataset"
    elif dataset_name == "cancer":
        data = load_breast_cancer()
        description = "Breast cancer classification dataset"
    else:
        raise ValueError("Dataset must be 'iris', 'wine', or 'cancer'")
    
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df['target'] = data.target
    df['target_name'] = [data.target_names[i] for i in data.target]
    
    return df, description, data.target_names

def train_model_with_cv(X_train, y_train, X_test, y_test, dataset_name):
    """Train a model with cross-validation and log to MLflow."""
    
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")
    
    # Create experiment
    experiment_name = f"Real Data - {dataset_name.title()} Classification"
    try:
        experiment_id = mlflow.create_experiment(experiment_name)
        print(f"Created new experiment: {experiment_name}")
    except:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id
        print(f"Using existing experiment: {experiment_name}")
    
    with mlflow.start_run(experiment_id=experiment_id) as run:
        print(f"Started MLflow run: {run.info.run_id}")
        
        # Train model with different hyperparameters
        n_estimators = 100
        max_depth = 10
        random_state = 42
        
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state
        )
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        # Train on full training set
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Log parameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("random_state", random_state)
        mlflow.log_param("dataset", dataset_name)
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("cv_mean", cv_mean)
        mlflow.log_metric("cv_std", cv_std)
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        # Log additional info
        mlflow.set_tag("model_type", "RandomForest")
        mlflow.set_tag("task", "classification")
        mlflow.set_tag("dataset", dataset_name)
        mlflow.set_tag("cross_validation", "5-fold")
        
        print(f"Model accuracy: {accuracy:.4f}")
        print(f"CV mean: {cv_mean:.4f} (+/- {cv_std:.4f})")
        print(f"Run ID: {run.info.run_id}")
        
        return model, run.info.run_id, accuracy

def main():
    """Main function to run the real data example."""
    print("=== Real Data MLOps Example ===")
    
    datasets = ["iris", "wine", "cancer"]
    results = []
    
    for dataset_name in datasets:
        print(f"\n--- Processing {dataset_name.upper()} Dataset ---")
        
        # Load dataset
        df, description, target_names = load_dataset(dataset_name)
        print(f"Dataset: {description}")
        print(f"Shape: {df.shape}")
        print(f"Features: {list(df.columns[:-2])}")
        print(f"Target classes: {list(target_names)}")
        
        # Prepare features and target
        X = df.drop(['target', 'target_name'], axis=1)
        y = df['target']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Train model and log to MLflow
        print("Training model and logging to MLflow...")
        model, run_id, accuracy = train_model_with_cv(X_train, y_train, X_test, y_test, dataset_name)
        
        # Test model prediction
        print("Testing model prediction...")
        sample_prediction = model.predict(X_test.head(1))
        sample_prob = model.predict_proba(X_test.head(1))
        predicted_class = target_names[sample_prediction[0]]
        
        print(f"Sample prediction: {predicted_class}")
        print(f"Prediction probabilities: {sample_prob[0]}")
        
        results.append({
            'dataset': dataset_name,
            'accuracy': accuracy,
            'run_id': run_id
        })
    
    print(f"\n=== Results Summary ===")
    for result in results:
        print(f"{result['dataset'].title()}: {result['accuracy']:.4f} (Run: {result['run_id'][:8]}...)")
    
    print(f"\n=== Example Complete ===")
    print(f"MLflow UI: http://localhost:5000")
    print("Check the MLflow UI to see all logged experiments!")

if __name__ == "__main__":
    main()
