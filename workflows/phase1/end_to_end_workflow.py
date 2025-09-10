"""
End-to-End MLOps Workflow Example
This demonstrates the complete workflow from data ingestion to model deployment
with full OpenLineage integration.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

# MLflow imports
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

# Feast imports
from feast import FeatureStore, Entity, Feature, FeatureView, ValueType
from feast.data_source import FileSource

# OpenLineage integrations
from integrations.mlflow_openlineage_integration import MLflowOpenLineagePlugin
from integrations.feast_openlineage_integration import FeastOpenLineagePlugin
from integrations.modelcatalogue_openlineage_integration import ModelCatalogueOpenLineagePlugin

# Model imports
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

logger = logging.getLogger(__name__)

class MLOpsWorkflow:
    """Complete MLOps workflow with OpenLineage integration."""
    
    def __init__(self):
        """Initialize the workflow with all integrations."""
        self.mlflow_plugin = MLflowOpenLineagePlugin()
        self.feast_plugin = FeastOpenLineagePlugin()
        self.modelcatalogue_plugin = ModelCatalogueOpenLineagePlugin()
        
        # Initialize MLflow
        mlflow.set_tracking_uri("http://localhost:5000")
        self.mlflow_client = MlflowClient()
        
        # Initialize Feast
        self.feast_store = FeatureStore(repo_path="./feast_repo")
        
    def step1_data_ingestion_and_feature_engineering(self) -> str:
        """Step 1: Ingest data and create features in Feast."""
        logger.info("Step 1: Data ingestion and feature engineering")
        
        # Create sample data
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic customer data
        customer_data = pd.DataFrame({
            'customer_id': range(1, n_samples + 1),
            'age': np.random.randint(18, 80, n_samples),
            'income': np.random.normal(50000, 15000, n_samples),
            'credit_score': np.random.randint(300, 850, n_samples),
            'transaction_amount': np.random.exponential(100, n_samples),
            'transaction_count': np.random.poisson(10, n_samples),
            'event_timestamp': [datetime.now() - timedelta(days=np.random.randint(0, 30)) 
                              for _ in range(n_samples)]
        })
        
        # Create target variable (loan approval)
        customer_data['loan_approved'] = (
            (customer_data['credit_score'] > 650) & 
            (customer_data['income'] > 40000) & 
            (customer_data['transaction_count'] > 5)
        ).astype(int)
        
        # Save data to file
        customer_data.to_parquet('./data/customer_data.parquet', index=False)
        
        # Define Feast entities and features
        customer_entity = Entity(
            name="customer_id",
            value_type=ValueType.INT64,
            description="Customer identifier"
        )
        
        # Create feature view
        customer_features = FeatureView(
            name="customer_features",
            entities=["customer_id"],
            ttl=timedelta(days=30),
            features=[
                Feature(name="age", dtype=ValueType.INT64),
                Feature(name="income", dtype=ValueType.FLOAT),
                Feature(name="credit_score", dtype=ValueType.INT64),
                Feature(name="transaction_amount", dtype=ValueType.FLOAT),
                Feature(name="transaction_count", dtype=ValueType.INT64),
            ],
            source=FileSource(
                path="./data/customer_data.parquet",
                timestamp_field="event_timestamp"
            )
        )
        
        # Apply feature view to Feast store
        self.feast_store.apply([customer_entity, customer_features])
        
        # Emit OpenLineage event for feature ingestion
        source_datasets = [{
            "name": "customer_data",
            "namespace": "raw_data",
            "source": "file_system",
            "uri": "./data/customer_data.parquet",
            "schema": [
                {"name": "customer_id", "type": "int64"},
                {"name": "age", "type": "int64"},
                {"name": "income", "type": "float64"},
                {"name": "credit_score", "type": "int64"},
                {"name": "transaction_amount", "type": "float64"},
                {"name": "transaction_count", "type": "int64"},
                {"name": "loan_approved", "type": "int64"}
            ]
        }]
        
        feature_schema = [
            {"name": "age", "type": "int64"},
            {"name": "income", "type": "float64"},
            {"name": "credit_score", "type": "int64"},
            {"name": "transaction_amount", "type": "float64"},
            {"name": "transaction_count", "type": "int64"}
        ]
        
        feature_ingestion_run_id = self.feast_plugin.log_feature_ingestion(
            "customer_features", source_datasets, feature_schema
        )
        
        logger.info(f"Feature ingestion completed with run_id: {feature_ingestion_run_id}")
        return feature_ingestion_run_id
        
    def step2_mlflow_experiment_setup(self) -> str:
        """Step 2: Set up MLflow experiment."""
        logger.info("Step 2: MLflow experiment setup")
        
        # Create experiment
        experiment_name = "loan_approval_prediction"
        experiment = mlflow.create_experiment(experiment_name)
        
        # Emit OpenLineage event for experiment start
        experiment_run_id = self.mlflow_plugin.log_experiment_start(
            experiment_id=experiment.experiment_id,
            experiment_name=experiment_name,
            user_id="data_scientist_1",
            tags={"project": "loan_approval", "team": "ml_team"}
        )
        
        logger.info(f"Experiment setup completed with run_id: {experiment_run_id}")
        return experiment_run_id
        
    def step3_model_training(self, experiment_id: str) -> str:
        """Step 3: Train model with feature consumption from Feast."""
        logger.info("Step 3: Model training")
        
        # Start MLflow run
        with mlflow.start_run(experiment_id=experiment_id) as run:
            run_id = run.info.run_id
            
            # Emit OpenLineage event for run start
            input_datasets = [{
                "name": "customer_data",
                "source": "feast",
                "uri": "feast://feature_view/customer_features"
            }]
            
            parameters = {
                "model_type": "RandomForestClassifier",
                "n_estimators": 100,
                "max_depth": 10,
                "random_state": 42
            }
            
            self.mlflow_plugin.log_run_start(
                run_id, experiment_id, input_datasets, parameters
            )
            
            # Log parameters
            mlflow.log_params(parameters)
            
            # Load data (simulating feature consumption from Feast)
            customer_data = pd.read_parquet('./data/customer_data.parquet')
            
            # Emit OpenLineage event for feature consumption
            feature_names = ["age", "income", "credit_score", "transaction_amount", "transaction_count"]
            self.mlflow_plugin.log_feature_consumption(
                run_id, feature_names, "feast://feature_view/customer_features"
            )
            
            # Prepare features and target
            feature_columns = ["age", "income", "credit_score", "transaction_amount", "transaction_count"]
            X = customer_data[feature_columns]
            y = customer_data["loan_approved"]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=parameters["n_estimators"],
                max_depth=parameters["max_depth"],
                random_state=parameters["random_state"]
            )
            
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            
            metrics = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall
            }
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.sklearn.log_model(
                model, "model", 
                input_example=X_train.head(1),
                signature=mlflow.models.infer_signature(X_train, y_train)
            )
            
            # Emit OpenLineage event for model training
            output_artifacts = [{
                "name": "model",
                "uri": f"mlflow://runs/{run_id}/artifacts/model"
            }]
            
            self.mlflow_plugin.log_model_training(
                run_id, "loan_approval_model", "RandomForestClassifier", 
                metrics, output_artifacts
            )
            
            logger.info(f"Model training completed with run_id: {run_id}")
            return run_id
            
    def step4_model_validation(self, run_id: str) -> Dict[str, Any]:
        """Step 4: Validate model performance."""
        logger.info("Step 4: Model validation")
        
        # Load model from MLflow
        model_uri = f"mlflow://runs/{run_id}/artifacts/model"
        model = mlflow.sklearn.load_model(model_uri)
        
        # Load test data
        customer_data = pd.read_parquet('./data/customer_data.parquet')
        feature_columns = ["age", "income", "credit_score", "transaction_amount", "transaction_count"]
        X = customer_data[feature_columns]
        y = customer_data["loan_approved"]
        
        # Validation checks
        validation_results = {
            "accuracy_threshold": 0.8,
            "precision_threshold": 0.75,
            "recall_threshold": 0.7
        }
        
        # Perform validation
        y_pred = model.predict(X)
        accuracy = accuracy_score(y, y_pred)
        precision = precision_score(y, y_pred)
        recall = recall_score(y, y_pred)
        
        validation_checks = [
            {
                "name": "accuracy_check",
                "passed": accuracy >= validation_results["accuracy_threshold"],
                "actual_value": accuracy,
                "expected_value": validation_results["accuracy_threshold"]
            },
            {
                "name": "precision_check", 
                "passed": precision >= validation_results["precision_threshold"],
                "actual_value": precision,
                "expected_value": validation_results["precision_threshold"]
            },
            {
                "name": "recall_check",
                "passed": recall >= validation_results["recall_threshold"],
                "actual_value": recall,
                "expected_value": validation_results["recall_threshold"]
            }
        ]
        
        # Emit OpenLineage event for model validation
        self.modelcatalogue_plugin.log_model_validation(
            "loan_approval_model", "v1.0", validation_results, validation_checks
        )
        
        logger.info("Model validation completed")
        return {
            "validation_passed": all(check["passed"] for check in validation_checks),
            "validation_results": validation_results,
            "validation_checks": validation_checks
        }
        
    def step5_model_registration(self, run_id: str, validation_passed: bool) -> str:
        """Step 5: Register model in ModelCatalogue if validation passes."""
        logger.info("Step 5: Model registration")
        
        if not validation_passed:
            logger.warning("Model validation failed, skipping registration")
            return None
            
        # Register model in MLflow
        model_name = "loan_approval_model"
        model_version = "v1.0"
        model_uri = f"mlflow://runs/{run_id}/artifacts/model"
        
        # Register in MLflow model registry
        registered_model = mlflow.register_model(
            model_uri, model_name
        )
        
        # Emit OpenLineage event for model registration
        model_metadata = {
            "model_type": "RandomForestClassifier",
            "feature_names": ["age", "income", "credit_score", "transaction_amount", "transaction_count"],
            "target_name": "loan_approved",
            "validation_passed": True
        }
        
        registration_run_id = self.modelcatalogue_plugin.log_model_registration(
            model_name, model_version, model_uri, "RandomForestClassifier",
            source_experiment_id=run_id, source_run_id=run_id,
            model_metadata=model_metadata
        )
        
        logger.info(f"Model registration completed with run_id: {registration_run_id}")
        return registration_run_id
        
    def step6_model_deployment(self, model_name: str, model_version: str) -> str:
        """Step 6: Deploy model to production."""
        logger.info("Step 6: Model deployment")
        
        deployment_environment = "production"
        deployment_config = {
            "replicas": 3,
            "resources": {
                "cpu": "500m",
                "memory": "1Gi"
            },
            "autoscaling": {
                "min_replicas": 2,
                "max_replicas": 10
            }
        }
        
        # Emit OpenLineage event for model deployment
        deployment_run_id = self.modelcatalogue_plugin.log_model_deployment(
            model_name, model_version, deployment_environment, deployment_config
        )
        
        logger.info(f"Model deployment completed with run_id: {deployment_run_id}")
        return deployment_run_id
        
    def run_complete_workflow(self):
        """Run the complete MLOps workflow."""
        logger.info("Starting complete MLOps workflow")
        
        try:
            # Step 1: Data ingestion and feature engineering
            feature_run_id = self.step1_data_ingestion_and_feature_engineering()
            
            # Step 2: MLflow experiment setup
            experiment_run_id = self.step2_mlflow_experiment_setup()
            
            # Step 3: Model training
            training_run_id = self.step3_model_training(experiment_run_id)
            
            # Step 4: Model validation
            validation_result = self.step4_model_validation(training_run_id)
            
            # Step 5: Model registration (if validation passes)
            if validation_result["validation_passed"]:
                registration_run_id = self.step5_model_registration(
                    training_run_id, validation_result["validation_passed"]
                )
                
                # Step 6: Model deployment
                deployment_run_id = self.step6_model_deployment(
                    "loan_approval_model", "v1.0"
                )
                
                logger.info("Complete MLOps workflow completed successfully")
                return {
                    "feature_run_id": feature_run_id,
                    "experiment_run_id": experiment_run_id,
                    "training_run_id": training_run_id,
                    "registration_run_id": registration_run_id,
                    "deployment_run_id": deployment_run_id,
                    "status": "success"
                }
            else:
                logger.error("Model validation failed, workflow stopped")
                return {
                    "feature_run_id": feature_run_id,
                    "experiment_run_id": experiment_run_id,
                    "training_run_id": training_run_id,
                    "status": "failed_validation"
                }
                
        except Exception as e:
            logger.error(f"Workflow failed with error: {str(e)}")
            raise

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create data directory
    os.makedirs('./data', exist_ok=True)
    os.makedirs('./feast_repo', exist_ok=True)
    
    # Run workflow
    workflow = MLOpsWorkflow()
    result = workflow.run_complete_workflow()
    
    print(f"Workflow result: {json.dumps(result, indent=2)}")
