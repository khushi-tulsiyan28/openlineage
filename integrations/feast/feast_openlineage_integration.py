import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from feast import FeatureStore
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

class FeastOpenLineageIntegration:
    
    def __init__(self, marquez_url: str = "http://localhost:5000"):
        self.client = OpenLineageClient(marquez_url)
        self.namespace = "feast"
        
    def emit_feature_ingestion(self, feature_view_name: str, 
                             source_datasets: List[Dict[str, Any]],
                             feature_schema: List[Dict[str, str]],
                             transformation_sql: str = None) -> str:
        run_id = f"feature_ingestion_{feature_view_name}_{datetime.now().isoformat()}"
        
        job = Job(
            namespace=self.namespace,
            name=f"feature_ingestion_{feature_view_name}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Feature ingestion for {feature_view_name}"
                ),
                "sourceCodeLocation": SourceCodeLocationJobFacet(
                    type="sql",
                    url=os.getenv("GIT_REPO_URL", ""),
                    revision=os.getenv("GIT_COMMIT_SHA", "")
                )
            }
        )
        
        if transformation_sql:
            job.facets["sql"] = {
                "query": transformation_sql
            }
        
        inputs = []
        for dataset in source_datasets:
            inputs.append(Dataset(
                namespace=dataset.get("namespace", "raw_data"),
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
        
        feature_dataset = Dataset(
            namespace=self.namespace,
            name=f"feature_view_{feature_view_name}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="feast_feature_store",
                    uri=f"feast://feature_view/{feature_view_name}"
                ),
                "schema": SchemaDatasetFacet(
                    fields=[
                        SchemaField(name=field["name"], type=field["type"])
                        for field in feature_schema
                    ]
                )
            }
        )
        
        run = Run(
            runId=run_id,
            facets={
                "feast": {
                    "feature_view_name": feature_view_name,
                    "transformation_type": "batch" if not transformation_sql else "sql",
                    "source_datasets": [d["name"] for d in source_datasets]
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.COMPLETE,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            inputs=inputs,
            outputs=[feature_dataset],
            producer="feast-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted feature ingestion event for {feature_view_name}")
        return run_id
        
    def emit_feature_serving(self, feature_view_name: str, 
                           entity_keys: List[str],
                           feature_names: List[str],
                           serving_type: str = "online") -> str:
        run_id = f"feature_serving_{feature_view_name}_{datetime.now().isoformat()}"
        
        job = Job(
            namespace=self.namespace,
            name=f"feature_serving_{feature_view_name}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Feature serving for {feature_view_name} ({serving_type})"
                )
            }
        )
        
        feature_dataset = Dataset(
            namespace=self.namespace,
            name=f"feature_view_{feature_view_name}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="feast_feature_store",
                    uri=f"feast://feature_view/{feature_view_name}"
                )
            }
        )
        
        served_features_dataset = Dataset(
            namespace=self.namespace,
            name=f"served_features_{feature_view_name}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="feast_serving",
                    uri=f"feast://served_features/{feature_view_name}"
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
            runId=run_id,
            facets={
                "feast": {
                    "feature_view_name": feature_view_name,
                    "serving_type": serving_type,
                    "entity_keys": entity_keys,
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
            outputs=[served_features_dataset],
            producer="feast-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted feature serving event for {feature_view_name}")
        return run_id
        
    def emit_feature_validation(self, feature_view_name: str,
                              validation_results: Dict[str, Any],
                              data_quality_checks: List[Dict[str, Any]]) -> str:
        run_id = f"feature_validation_{feature_view_name}_{datetime.now().isoformat()}"
        
        job = Job(
            namespace=self.namespace,
            name=f"feature_validation_{feature_view_name}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Feature validation for {feature_view_name}"
                )
            }
        )
        
        feature_dataset = Dataset(
            namespace=self.namespace,
            name=f"feature_view_{feature_view_name}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="feast_feature_store",
                    uri=f"feast://feature_view/{feature_view_name}"
                ),
                "dataQualityAssertions": DataQualityAssertionsDatasetFacet(
                    assertions=[
                        DataQualityAssertion(
                            assertion=Assertion(
                                assertion=check["name"],
                                column=check.get("column"),
                                threshold=check.get("threshold")
                            ),
                            result=AssertionResult(
                                passed=check["passed"],
                                actualValue=check.get("actual_value"),
                                expectedValue=check.get("expected_value")
                            )
                        )
                        for check in data_quality_checks
                    ]
                )
            }
        )
        
        run = Run(
            runId=run_id,
            facets={
                "feast": {
                    "feature_view_name": feature_view_name,
                    "validation_results": validation_results,
                    "data_quality_checks": data_quality_checks
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.COMPLETE,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            inputs=[feature_dataset],
            producer="feast-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted feature validation event for {feature_view_name}")
        return run_id
        
    def emit_feature_transformation(self, source_feature_view: str,
                                  target_feature_view: str,
                                  transformation_code: str,
                                  transformation_type: str = "python") -> str:
        run_id = f"feature_transformation_{source_feature_view}_to_{target_feature_view}_{datetime.now().isoformat()}"
        
        job = Job(
            namespace=self.namespace,
            name=f"feature_transformation_{source_feature_view}_to_{target_feature_view}",
            facets={
                "documentation": DocumentationJobFacet(
                    description=f"Feature transformation from {source_feature_view} to {target_feature_view}"
                ),
                "sourceCodeLocation": SourceCodeLocationJobFacet(
                    type=transformation_type,
                    url=os.getenv("GIT_REPO_URL", ""),
                    revision=os.getenv("GIT_COMMIT_SHA", "")
                )
            }
        )
        
        input_dataset = Dataset(
            namespace=self.namespace,
            name=f"feature_view_{source_feature_view}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="feast_feature_store",
                    uri=f"feast://feature_view/{source_feature_view}"
                )
            }
        )
        
        output_dataset = Dataset(
            namespace=self.namespace,
            name=f"feature_view_{target_feature_view}",
            facets={
                "dataSource": DataSourceDatasetFacet(
                    name="feast_feature_store",
                    uri=f"feast://feature_view/{target_feature_view}"
                )
            }
        )
        
        run = Run(
            runId=run_id,
            facets={
                "feast": {
                    "source_feature_view": source_feature_view,
                    "target_feature_view": target_feature_view,
                    "transformation_type": transformation_type,
                    "transformation_code": transformation_code
                }
            }
        )
        
        event = RunEvent(
            eventType=RunEventType.COMPLETE,
            eventTime=datetime.now().isoformat(),
            run=run,
            job=job,
            inputs=[input_dataset],
            outputs=[output_dataset],
            producer="feast-openlineage-integration"
        )
        
        self.client.emit(event)
        logger.info(f"Emitted feature transformation event from {source_feature_view} to {target_feature_view}")
        return run_id

# Feast plugin integration
class FeastOpenLineagePlugin:
    
    def __init__(self):
        self.integration = FeastOpenLineageIntegration()
        
    def log_feature_ingestion(self, feature_view_name: str, 
                            source_datasets: List[Dict[str, Any]],
                            feature_schema: List[Dict[str, str]],
                            transformation_sql: str = None):
        return self.integration.emit_feature_ingestion(
            feature_view_name, source_datasets, feature_schema, transformation_sql
        )
        
    def log_feature_serving(self, feature_view_name: str, 
                          entity_keys: List[str],
                          feature_names: List[str],
                          serving_type: str = "online"):
        return self.integration.emit_feature_serving(
            feature_view_name, entity_keys, feature_names, serving_type
        )
        
    def log_feature_validation(self, feature_view_name: str,
                             validation_results: Dict[str, Any],
                             data_quality_checks: List[Dict[str, Any]]):
        return self.integration.emit_feature_validation(
            feature_view_name, validation_results, data_quality_checks
        )
        
    def log_feature_transformation(self, source_feature_view: str,
                                 target_feature_view: str,
                                 transformation_code: str,
                                 transformation_type: str = "python"):
        return self.integration.emit_feature_transformation(
            source_feature_view, target_feature_view, transformation_code, transformation_type
        )
