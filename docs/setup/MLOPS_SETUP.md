# MLOps Platform with OpenLineage Integration

## Overview

This repository contains a complete MLOps platform architecture that integrates:

- **MLflow** - Experiment tracking & model lifecycle management
- **Feast** - Feature store (backed by S3/blob + Postgres)
- **ModelCatalogue** - Model registry and discovery
- **API Gateway** - OAuth-based authentication/authorization
- **Marquez** - Central lineage/metadata store (OpenLineage backend)

## Architecture

The platform provides end-to-end lineage tracking from raw data ingestion to model deployment, with Marquez serving as the central metadata store powered by OpenLineage.

### Key Features

- **Complete Lineage Tracking**: Every data transformation and model operation is tracked
- **OAuth Authentication**: Secure access through API Gateway
- **Feature Store Integration**: Point-in-time correct features with Feast
- **Model Lifecycle Management**: From experiment to production deployment
- **Centralized Metadata**: Single source of truth for all lineage information

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Java 17 (for Marquez)

### 1. Start the Platform

```bash
# Start all services
docker-compose -f docker-compose-mlops.yml up -d

# Verify services are running
docker-compose -f docker-compose-mlops.yml ps
```

### 2. Access the Services

- **Marquez Web UI**: http://localhost:5000
- **MLflow UI**: http://localhost:5002
- **Feast Feature Server**: http://localhost:6566
- **ModelCatalogue**: http://localhost:8080
- **API Gateway**: http://localhost:8081
- **Jupyter Notebook**: http://localhost:8888

### 3. Run the End-to-End Workflow

```bash
# Execute the complete workflow
python workflows/end_to_end_workflow.py
```

### 4. Query Lineage Information

```bash
# Run OpenLineage query examples
python examples/openlineage_queries.py
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# API Gateway OAuth
API_GATEWAY_CLIENT_SECRET=your_client_secret

# MLflow
MLFLOW_CLIENT_SECRET=your_mlflow_secret

# Feast
FEAST_CLIENT_SECRET=your_feast_secret

# ModelCatalogue
MODELCATALOGUE_CLIENT_SECRET=your_modelcatalogue_secret

# Git Information (for lineage tracking)
GIT_REPO_URL=https://github.com/your-org/your-repo
GIT_COMMIT_SHA=your_commit_sha
```

### Service Configuration

Each service has its own configuration file in the `configs/` directory:

- `mlflow-openlineage-config.yaml` - MLflow configuration
- `feast-openlineage-config.yaml` - Feast configuration
- `modelcatalogue-openlineage-config.yaml` - ModelCatalogue configuration
- `api-gateway-oauth-config.yaml` - API Gateway configuration

## Workflow Description

### 1. Data Ingestion and Feature Engineering

1. Raw data is ingested from various sources
2. Data is cleaned, validated, and transformed into features
3. Features are stored in Feast with point-in-time correctness
4. OpenLineage events are emitted for all transformations

### 2. MLflow Experiment Setup

1. Data scientist creates a new MLflow experiment
2. Experiment metadata is logged with tags and descriptions
3. OpenLineage events track experiment creation

### 3. Model Training with Feature Consumption

1. MLflow run is started within the experiment
2. Features are consumed from Feast feature store
3. Model training is performed with hyperparameter tuning
4. Training metrics and model artifacts are logged
5. OpenLineage events track feature consumption and model training

### 4. Model Validation

1. Trained model is validated against business criteria
2. Data quality and model quality checks are performed
3. OpenLineage events track validation results

### 5. Model Registration

1. If validation passes, model is registered in ModelCatalogue
2. Model metadata is linked to source experiment and features
3. OpenLineage events track model registration and metadata linking

### 6. Model Deployment

1. Model is deployed to production environment
2. Deployment configuration is applied
3. OpenLineage events track deployment and serving endpoints

## Lineage Tracking

### OpenLineage Events

The platform emits OpenLineage events for:

- **Dataset Events**: Raw data, features, model artifacts
- **Job Events**: Data processing, model training, validation, deployment
- **Run Events**: Individual execution instances
- **Facet Events**: Metadata, schemas, quality metrics

### Event Flow

```
All Services → OpenLineage Events → Marquez → Centralized Lineage Graph
```

### Querying Lineage

Use the Marquez API to query lineage information:

```python
from examples.openlineage_queries import MarquezQueryClient

client = MarquezQueryClient("http://localhost:5000")

# Get model lineage
model_lineage = client.get_lineage_for_model("loan_approval_model")

# Get impact analysis
impact = client.get_impact_analysis("customer_data", "raw_data")

# Search datasets
results = client.search_datasets("customer")
```

## Integration Examples

### MLflow Integration

```python
from integrations.mlflow_openlineage_integration import MLflowOpenLineagePlugin

plugin = MLflowOpenLineagePlugin()

# Emit experiment start event
experiment_run_id = plugin.log_experiment_start(
    experiment_id="exp_123",
    experiment_name="loan_approval",
    user_id="data_scientist_1"
)

# Emit feature consumption event
plugin.log_feature_consumption(
    run_id="run_456",
    feature_names=["age", "income", "credit_score"],
    feature_store_uri="feast://feature_view/customer_features"
)
```

### Feast Integration

```python
from integrations.feast_openlineage_integration import FeastOpenLineagePlugin

plugin = FeastOpenLineagePlugin()

# Emit feature ingestion event
ingestion_run_id = plugin.log_feature_ingestion(
    feature_view_name="customer_features",
    source_datasets=[{
        "name": "customer_data",
        "namespace": "raw_data",
        "source": "file_system",
        "uri": "./data/customer_data.parquet"
    }],
    feature_schema=[
        {"name": "age", "type": "int64"},
        {"name": "income", "type": "float64"}
    ]
)
```

### ModelCatalogue Integration

```python
from integrations.modelcatalogue_openlineage_integration import ModelCatalogueOpenLineagePlugin

plugin = ModelCatalogueOpenLineagePlugin()

# Emit model registration event
registration_run_id = plugin.log_model_registration(
    model_name="loan_approval_model",
    model_version="v1.0",
    model_uri="mlflow://runs/run_456/artifacts/model",
    model_type="RandomForestClassifier",
    source_experiment_id="exp_123"
)
```

## Monitoring and Alerting

### Key Metrics

- **Lineage Event Volume**: Number of events per service
- **Event Processing Latency**: Time from event emission to storage
- **Data Quality Metrics**: Validation results and quality scores
- **Model Performance**: Accuracy, precision, recall trends
- **Feature Usage**: Most consumed features and their impact

### Alerting Rules

- **Missing Lineage Events**: Alert if expected events are not received
- **Data Quality Degradation**: Alert if validation scores drop
- **Model Performance Drift**: Alert if model metrics degrade
- **Feature Store Issues**: Alert if feature serving fails
- **Deployment Failures**: Alert if model deployment fails

## Troubleshooting

### Common Issues

1. **Marquez Connection Issues**
   ```bash
   # Check if Marquez is running
   curl http://localhost:5000/api/v1/namespaces
   ```

2. **MLflow Tracking Issues**
   ```bash
   # Check MLflow server status
   curl http://localhost:5002/health
   ```

3. **Feast Feature Store Issues**
   ```bash
   # Check Feast server status
   curl http://localhost:6566/health
   ```

4. **Docker Compose Issues**
   ```bash
   # View logs for specific service
   docker-compose -f docker-compose-mlops.yml logs mlflow
   ```

### Logs

View logs for specific services:

```bash
# MLflow logs
docker-compose -f docker-compose-mlops.yml logs mlflow

# Feast logs
docker-compose -f docker-compose-mlops.yml logs feast

# Marquez logs
docker-compose -f docker-compose-mlops.yml logs marquez
```

## Development

### Adding New Integrations

1. Create a new integration class in `integrations/`
2. Implement OpenLineage event emission methods
3. Add configuration in `configs/`
4. Update Docker Compose configuration
5. Add tests and documentation

### Extending Lineage Tracking

1. Identify new data sources or transformations
2. Add OpenLineage event emission points
3. Update lineage queries and examples
4. Test with end-to-end workflow

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Support

For questions and support:

- Create an issue in the repository
- Check the troubleshooting section
- Review the OpenLineage documentation
- Consult the Marquez documentation
