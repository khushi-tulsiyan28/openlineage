import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import mlflow
from mlflow.tracking import MlflowClient
from openlineage.client import OpenLineageClient
from openlineage.client.facet import (
    DataSourceDatasetFacet,
    SchemaDatasetFacet,
    SchemaField,
    DocumentationJobFacet,
    SourceCodeLocationJobFacet,
    SqlJobFacet,
    DataQualityAssertionsDatasetFacet,
    DataQualityAssertion,
    Assertion,
    AssertionResult
)
from openlineage.client.run import RunEvent, RunState, Run, Job, Dataset
from openlineage.client.run import RunEventType

logger = logging.getLogger(__name__)

class MLflowOpenLineageIntegration:
    
    def __init__(self, marquez_url: str = "http://localhost:5000"):
        self.client = OpenLineageClient(marquez_url)
        self.namespace = "mlflow"
        self.mlflow_client = MlflowClient()
        
    def emit_experiment_start(self, experiment_id: str, experiment_name: str, 
                            user_id: str, tags: Dict[str, str] = None) -> str:
        run_id = f"experiment_{experiment_id}_{datetime.now().isoformat()}"
        
        job = Job(
            namespace=self.namespace,
            name=f"experiment_{experiment_name}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"MLflow experiment: {experiment_name}"
                ),
                "sourceCodeLocation": SourceCodeLocationJobFacet(
                    type="git",
                    url=os.getenv("GIT_REPO_URL", ""),
                    revision=os.getenv("GIT_COMMIT_SHA", "")
                )
            }
        )
        
        run = Run(
            runId=run_id,
            facets={
                "mlflow": {
                    "experiment_id": experiment_id,
                    "experiment_name": experiment_name,
                    "user_id": user_id,
                    "tags": tags or {}
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.START,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            producer="mlflow-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted experiment start event for {experiment_name}")
        return run_id
        
    def emit_run_start(self, run_id: str, experiment_id: str, 
                      input_datasets: List[Dict[str, Any]] = None,
                      parameters: Dict[str, Any] = None) -> None:
        job = Job(
            namespace=self.namespace,
            name=f"run_{run_id}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"MLflow run: {run_id}"
                )
            }
        )
        
        inputs = []
        if input_datasets:
            for dataset in input_datasets:
                inputs.append(Dataset(
                    namespace=self.namespace,
                    name=dataset["name"],
                    facets={
                        "dataSource": DataSourceDatasetFacet(
                            name=dataset.get("source", "unknown"),
                            uri=dataset.get("uri", "")
                        ),
                        "schema": SchemaDatasetFacet(
                            fields=[
                                SchemaField(name=field["name"], type=field["type"])
                                for field in dataset.get("schema", [])
                            ]
                        )
                    }
                ))
        
        run = Run(
            runId=run_id,
            facets={
                "mlflow": {
                    "experiment_id": experiment_id,
                    "parameters": parameters or {}
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.START,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            inputs=inputs,
            producer="mlflow-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted run start event for {run_id}")
        
    def emit_feature_consumption(self, run_id: str, feature_names: List[str], 
                               feature_store_uri: str) -> None:
        job = Job(
            namespace=self.namespace,
            name=f"feature_consumption_{run_id}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Feature consumption from Feast for run {run_id}"
                )
            }
        )
        
        feature_dataset = Dataset(
            namespace="feast",
            name="feature_store",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="feast",
                    uri=feature_store_uri
                ),
                "schema": SchemaDatasetFacet(
                    fields=[
                        SchemaField(name=name, type="feature")
                        for name in feature_names
                    ]
                )
            }
        )
        
        run = Run(
            runId=f"{run_id}_features",
            facets={
                "mlflow": {
                    "parent_run_id": run_id,
                    "feature_names": feature_names
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.START,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            inputs=[feature_dataset],
            producer="mlflow-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted feature consumption event for {run_id}")
        
    def emit_model_training(self, run_id: str, model_name: str, 
                          model_type: str, metrics: Dict[str, float],
                          output_artifacts: List[Dict[str, str]] = None) -> None:
        job = Job(
            namespace=self.namespace,
            name=f"model_training_{run_id}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Model training: {model_name}"
                )
            }
        )
        
        outputs = []
        if output_artifacts:
            for artifact in output_artifacts:
                outputs.append(Dataset(
                    namespace=self.namespace,
                    name=artifact["name"],
                    facets={
                        "dataSource": DataSourceDatasetFacet(
                            name="mlflow_artifacts",
                            uri=artifact["uri"]
                        )
                    }
                ))
        
        run = Run(
            runId=f"{run_id}_training",
            facets={
                "mlflow": {
                    "parent_run_id": run_id,
                    "model_name": model_name,
                    "model_type": model_type,
                    "metrics": metrics
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.COMPLETE,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            outputs=outputs,
            producer="mlflow-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted model training event for {run_id}")
        
    def emit_model_registration(self, run_id: str, model_name: str, 
                              model_version: str, model_uri: str,
                              modelcatalogue_id: str = None) -> None:
        job = Job(
            namespace="modelcatalogue",
            name=f"model_registration_{model_name}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Model registration: {model_name} v{model_version}"
                )
            }
        )
        
        model_dataset = Dataset(
            namespace="modelcatalogue",
            name=f"model_{model_name}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="modelcatalogue",
                    uri=model_uri
                ),
                "schema": SchemaDatasetFacet(
                    fields=[
                        SchemaField(name="model_name", type="string"),
                        SchemaField(name="model_version", type="string"),
                        SchemaField(name="model_uri", type="string")
                    ]
                )
            }
        )
        
        run = Run(
            runId=f"registration_{run_id}",
            facets={
                "modelcatalogue": {
                    "model_name": model_name,
                    "model_version": model_version,
                    "model_uri": model_uri,
                    "modelcatalogue_id": modelcatalogue_id
                },
                "mlflow": {
                    "source_run_id": run_id
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.COMPLETE,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            outputs=[model_dataset],
            producer="mlflow-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted model registration event for {model_name}")

class MLflowOpenLineagePlugin:
    
    def __init__(self):
        self.integration = MLflowOpenLineageIntegration()
        
    def log_experiment_start(self, experiment_id: str, experiment_name: str, 
                           user_id: str, tags: Dict[str, str] = None):
        return self.integration.emit_experiment_start(
            experiment_id, experiment_name, user_id, tags
        )
        
    def log_run_start(self, run_id: str, experiment_id: str, 
                     input_datasets: List[Dict[str, Any]] = None,
                     parameters: Dict[str, Any] = None):
        self.integration.emit_run_start(
            run_id, experiment_id, input_datasets, parameters
        )
        
    def log_feature_consumption(self, run_id: str, feature_names: List[str], 
                              feature_store_uri: str):
        self.integration.emit_feature_consumption(
            run_id, feature_names, feature_store_uri
        )
        
    def log_model_training(self, run_id: str, model_name: str, 
                         model_type: str, metrics: Dict[str, float],
                         output_artifacts: List[Dict[str, str]] = None):
        self.integration.emit_model_training(
            run_id, model_name, model_type, metrics, output_artifacts
        )
        
    def log_model_registration(self, run_id: str, model_name: str, 
                             model_version: str, model_uri: str,
                             modelcatalogue_id: str = None):
        self.integration.emit_model_registration(
            run_id, model_name, model_version, model_uri, modelcatalogue_id
        )
