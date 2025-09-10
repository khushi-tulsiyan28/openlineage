import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from openlineage.client import OpenLineageClient
from openlineage.client.facet import (
    DataSourceDatasetFacet,
    SchemaDatasetFacet,
    SchemaField,
    DocumentationJobFacet,
    SourceCodeLocationJobFacet,
    DataQualityAssertionsDatasetFacet,
    DataQualityAssertion,
    Assertion,
    AssertionResult
)
from openlineage.client.run import RunEvent, RunState, Run, Job, Dataset
from openlineage.client.run import RunEventType

logger = logging.getLogger(__name__)

class ModelCatalogueOpenLineageIntegration:
    
    def __init__(self, marquez_url: str = "http://localhost:5000"):
        self.client = OpenLineageClient(marquez_url)
        self.namespace = "modelcatalogue"
        
    def emit_model_registration(self, model_name: str, model_version: str,
                              model_uri: str, model_type: str,
                              source_experiment_id: str = None,
                              source_run_id: str = None,
                              model_metadata: Dict[str, Any] = None) -> str:
        run_id = f"model_registration_{model_name}_{model_version}_{datetime.now().isoformat()}"
        
        job = Job(
            namespace=self.namespace,
            name=f"model_registration_{model_name}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Model registration: {model_name} v{model_version}"
                ),
                "sourceCodeLocation": SourceCodeLocationJobFacet(
                    type="model",
                    url=os.getenv("GIT_REPO_URL", ""),
                    revision=os.getenv("GIT_COMMIT_SHA", "")
                )
            }
        )
        
        inputs = []
        if source_run_id:
            inputs.append(Dataset(
                namespace="mlflow",
                name=f"run_{source_run_id}",
                facets={
                    "dataSource": DataSourceDatasetFacet(
                        name="mlflow",
                        uri=f"mlflow://runs/{source_run_id}"
                    )
                }
            ))
        
        model_dataset = Dataset(
            namespace=self.namespace,
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
                        SchemaField(name="model_type", type="string"),
                        SchemaField(name="model_uri", type="string")
                    ]
                )
            }
        )
        
        run = Run(
            runId=run_id,
            facets={
                "modelcatalogue": {
                    "model_name": model_name,
                    "model_version": model_version,
                    "model_type": model_type,
                    "model_uri": model_uri,
                    "model_metadata": model_metadata or {}
                },
                "mlflow": {
                    "source_experiment_id": source_experiment_id,
                    "source_run_id": source_run_id
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.COMPLETE,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            inputs=inputs,
            outputs=[model_dataset],
            producer="modelcatalogue-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted model registration event for {model_name} v{model_version}")
        return run_id
        
    def emit_model_validation(self, model_name: str, model_version: str,
                            validation_results: Dict[str, Any],
                            validation_checks: List[Dict[str, Any]]) -> str:
        run_id = f"model_validation_{model_name}_{model_version}_{datetime.now().isoformat()}"
        
        job = Job(
            namespace=self.namespace,
            name=f"model_validation_{model_name}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Model validation: {model_name} v{model_version}"
                )
            }
        )
        
        model_dataset = Dataset(
            namespace=self.namespace,
            name=f"model_{model_name}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="modelcatalogue",
                    uri=f"modelcatalogue://models/{model_name}/{model_version}"
                ),
                "dataQualityAssertions": DataQualityAssertionsDatasetFacet(
                    assertions=[
                        DataQualityAssertion(
                            assertion=Assertion(
                                assertion=check["name"],
                                threshold=check.get("threshold")
                            ),
                            result=AssertionResult(
                                passed=check["passed"],
                                actualValue=check.get("actual_value"),
                                expectedValue=check.get("expected_value")
                            )
                        )
                        for check in validation_checks
                    ]
                )
            }
        )
        
        run = Run(
            runId=run_id,
            facets={
                "modelcatalogue": {
                    "model_name": model_name,
                    "model_version": model_version,
                    "validation_results": validation_results,
                    "validation_checks": validation_checks
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.COMPLETE,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            inputs=[model_dataset],
            producer="modelcatalogue-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted model validation event for {model_name} v{model_version}")
        return run_id
        
    def emit_model_deployment(self, model_name: str, model_version: str,
                            deployment_environment: str,
                            deployment_config: Dict[str, Any]) -> str:
        run_id = f"model_deployment_{model_name}_{model_version}_{datetime.now().isoformat()}"
        
        job = Job(
            namespace=self.namespace,
            name=f"model_deployment_{model_name}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Model deployment: {model_name} v{model_version} to {deployment_environment}"
                )
            }
        )
        
        model_dataset = Dataset(
            namespace=self.namespace,
            name=f"model_{model_name}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="modelcatalogue",
                    uri=f"modelcatalogue://models/{model_name}/{model_version}"
                )
            }
        )
        
        deployment_dataset = Dataset(
            namespace=self.namespace,
            name=f"deployment_{model_name}_{deployment_environment}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="deployment_platform",
                    uri=f"deployment://{deployment_environment}/{model_name}/{model_version}"
                )
            }
        )
        
        run = Run(
            runId=run_id,
            facets={
                "modelcatalogue": {
                    "model_name": model_name,
                    "model_version": model_version,
                    "deployment_environment": deployment_environment,
                    "deployment_config": deployment_config
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.COMPLETE,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            inputs=[model_dataset],
            outputs=[deployment_dataset],
            producer="modelcatalogue-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted model deployment event for {model_name} v{model_version}")
        return run_id
        
    def emit_model_retirement(self, model_name: str, model_version: str,
                            retirement_reason: str,
                            retirement_date: str) -> str:
        run_id = f"model_retirement_{model_name}_{model_version}_{datetime.now().isoformat()}"
        
        job = Job(
            namespace=self.namespace,
            name=f"model_retirement_{model_name}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Model retirement: {model_name} v{model_version}"
                )
            }
        )
        
        model_dataset = Dataset(
            namespace=self.namespace,
            name=f"model_{model_name}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="modelcatalogue",
                    uri=f"modelcatalogue://models/{model_name}/{model_version}"
                )
            }
        )
        
        run = Run(
            runId=run_id,
            facets={
                "modelcatalogue": {
                    "model_name": model_name,
                    "model_version": model_version,
                    "retirement_reason": retirement_reason,
                    "retirement_date": retirement_date
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.COMPLETE,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            inputs=[model_dataset],
            producer="modelcatalogue-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted model retirement event for {model_name} v{model_version}")
        return run_id
        
    def emit_model_performance_monitoring(self, model_name: str, model_version: str,
                                        performance_metrics: Dict[str, float],
                                        monitoring_period: str) -> str:
        run_id = f"model_monitoring_{model_name}_{model_version}_{datetime.now().isoformat()}"
        
        job = Job(
            namespace=self.namespace,
            name=f"model_monitoring_{model_name}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Model performance monitoring: {model_name} v{model_version}"
                )
            }
        )
        
        model_dataset = Dataset(
            namespace=self.namespace,
            name=f"model_{model_name}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="modelcatalogue",
                    uri=f"modelcatalogue://models/{model_name}/{model_version}"
                )
            }
        )
        
        monitoring_dataset = Dataset(
            namespace=self.namespace,
            name=f"monitoring_{model_name}_{model_version}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="monitoring_system",
                    uri=f"monitoring://models/{model_name}/{model_version}"
                )
            }
        )
        
        run = Run(
            runId=run_id,
            facets={
                "modelcatalogue": {
                    "model_name": model_name,
                    "model_version": model_version,
                    "performance_metrics": performance_metrics,
                    "monitoring_period": monitoring_period
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.COMPLETE,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            inputs=[model_dataset],
            outputs=[monitoring_dataset],
            producer="modelcatalogue-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted model monitoring event for {model_name} v{model_version}")
        return run_id

# ModelCatalogue plugin integration
class ModelCatalogueOpenLineagePlugin:
    
    def __init__(self):
        self.integration = ModelCatalogueOpenLineageIntegration()
        
    def log_model_registration(self, model_name: str, model_version: str,
                             model_uri: str, model_type: str,
                             source_experiment_id: str = None,
                             source_run_id: str = None,
                             model_metadata: Dict[str, Any] = None):
        return self.integration.emit_model_registration(
            model_name, model_version, model_uri, model_type,
            source_experiment_id, source_run_id, model_metadata
        )
        
    def log_model_validation(self, model_name: str, model_version: str,
                           validation_results: Dict[str, Any],
                           validation_checks: List[Dict[str, Any]]):
        return self.integration.emit_model_validation(
            model_name, model_version, validation_results, validation_checks
        )
        
    def log_model_deployment(self, model_name: str, model_version: str,
                           deployment_environment: str,
                           deployment_config: Dict[str, Any]):
        return self.integration.emit_model_deployment(
            model_name, model_version, deployment_environment, deployment_config
        )
        
    def log_model_retirement(self, model_name: str, model_version: str,
                           retirement_reason: str, retirement_date: str):
        return self.integration.emit_model_retirement(
            model_name, model_version, retirement_reason, retirement_date
        )
        
    def log_model_performance_monitoring(self, model_name: str, model_version: str,
                                       performance_metrics: Dict[str, float],
                                       monitoring_period: str):
        return self.integration.emit_model_performance_monitoring(
            model_name, model_version, performance_metrics, monitoring_period
        )
