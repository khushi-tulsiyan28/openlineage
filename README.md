# MLOps Platform with OpenLineage Integration

A comprehensive MLOps platform that integrates MLflow, Feast, ModelCatalogue, and Marquez for complete data lineage tracking from raw data to deployed models.

## 🏗️ Architecture Overview

This repository contains a two-phase MLOps platform:

- **Phase 1**: Core ML platform without OpenLineage integration (simplified setup)
- **Phase 2**: Full platform with OpenLineage integration and Marquez backend

## 📁 Repository Structure

```
openlineage/
├── docs/                           # Documentation
│   ├── architecture/               # Architecture documentation
│   │   ├── phase1-architecture.md
│   │   └── mlops-architecture.md
│   ├── setup/                      # Setup guides
│   │   └── MLOPS_SETUP.md
│   └── workflows/                  # Workflow documentation
│       └── workflow_narrative.md
├── configs/                        # Configuration files
│   ├── phase1/                     # Phase 1 configurations
│   │   └── .env.example
│   └── phase2/                     # Phase 2 configurations (future)
├── integrations/                   # OpenLineage integrations
│   ├── mlflow/                     # MLflow integration
│   │   └── mlflow_openlineage_integration.py  #needs to be an entire application and not a .py file because it will be a model-catalogue like huggingface
│   ├── feast/                      # Feast integration
│   │   └── feast_openlineage_integration.py
│   └── modelcatalogue/             # ModelCatalogue integration
│       └── modelcatalogue_openlineage_integration.py
├── examples/                       # Example code
│   ├── basic/                      # Basic examples
│   │   └── openlineage_queries.py
│   └── advanced/                   # Advanced examples (future)
├── workflows/                      # Workflow implementations
│   ├── phase1/                     # Phase 1 workflows
│   │   └── end_to_end_workflow.py
│   └── phase2/                     # Phase 2 workflows (future)
├── scripts/                        # Utility scripts
│   ├── setup/                      # Setup scripts
│   │   ├── start-phase1.sh
│   │   └── stop-phase1.sh
│   └── deployment/                 # Deployment scripts (future)
├── docker-compose.yml              # Phase 1 Docker Compose
└── README.md                       # This file
```

## 🚀 Quick Start - Phase 1

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for running examples)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd openlineage
```

### 2. Configure Environment

```bash
cp configs/phase1/.env.example .env
# Edit .env with your configuration
```

### 2.1. Configure Entra ID Authentication (Required)

The API Gateway now requires Microsoft Entra ID (Azure AD) authentication. Follow these steps:

1. **Set up Entra ID App Registration** (see [Entra ID Setup Guide](docs/setup/ENTRA_ID_SETUP.md))
2. **Configure environment variables**:
   ```bash
   # Add to your .env file
   ENTRA_TENANT_ID=your-tenant-id
   ENTRA_CLIENT_ID=your-client-id
   ENTRA_CLIENT_SECRET=your-client-secret
   ENTRA_AUDIENCE=api://your-client-id
   OAUTH_REDIRECT_URI=http://localhost:8081/oauth/callback
   ```

### 3. Start the Platform

```bash
# Using the setup script
./scripts/setup/start-phase1.sh

# Or manually
docker-compose up -d
```

### 4. Access Services

- **MLflow UI**: http://localhost:5000
- **ModelCatalogue**: http://localhost:8080
- **API Gateway**: http://localhost:8081
- **Jupyter Notebook**: http://localhost:8888
- **MinIO Console**: http://localhost:9001

### 5. Run Example Workflow

```bash
python workflows/phase1/end_to_end_workflow.py
```

## 🔧 Phase 1 Components

### Core Services

- **PostgreSQL**: Centralized metadata storage
- **Redis**: High-performance caching for Feast
- **MinIO**: S3-compatible object storage
- **MLflow**: Experiment tracking and model registry
- **ModelCatalogue**: Model discovery and lifecycle management
- **API Gateway**: OAuth authentication and request routing
- **Jupyter**: Containerized execution environment

### Key Features

- ✅ **Simplified Setup**: Single docker-compose file
- ✅ **Service Isolation**: Clear boundaries between components
- ✅ **Health Checks**: Automatic service monitoring
- ✅ **Mock Services**: Fast prototyping without external dependencies
- ✅ **Development Ready**: Easy local setup and testing

## 📚 Documentation

### Architecture

- [Phase 1 Architecture](docs/architecture/phase1-architecture.md) - Simplified architecture without OpenLineage
- [MLOps Architecture](docs/architecture/mlops-architecture.md) - Complete architecture with OpenLineage
- [Phase 1 Implementation Document](docs/PHASE1_IMPLEMENTATION_DOCUMENT.md) - Detailed implementation guide

### Setup and Usage

- [MLOps Setup Guide](docs/setup/MLOPS_SETUP.md) - Complete setup instructions
- [Workflow Narrative](docs/workflows/workflow_narrative.md) - End-to-end workflow description

### Examples

- [OpenLineage Queries](examples/basic/openlineage_queries.py) - Query lineage information
- [End-to-End Workflow](workflows/phase1/end_to_end_workflow.py) - Complete MLOps workflow

## 🔌 OpenLineage Integrations

### MLflow Integration

```python
from integrations.mlflow.mlflow_openlineage_integration import MLflowOpenLineagePlugin

plugin = MLflowOpenLineagePlugin()
plugin.log_experiment_start("exp_123", "loan_approval", "user_1")
```

### Feast Integration

```python
from integrations.feast.feast_openlineage_integration import FeastOpenLineagePlugin

plugin = FeastOpenLineagePlugin()
plugin.log_feature_ingestion("customer_features", source_datasets, feature_schema)
```

### ModelCatalogue Integration

```python
from integrations.modelcatalogue.modelcatalogue_openlineage_integration import ModelCatalogueOpenLineagePlugin

plugin = ModelCatalogueOpenLineagePlugin()
plugin.log_model_registration("model_1", "v1.0", "s3://models/model.pkl", "RandomForest")
```

## 🛠️ Development

### Adding New Integrations

1. Create integration class in `integrations/[service]/`
2. Implement OpenLineage event emission methods
3. Add configuration in `configs/`
4. Update Docker Compose configuration
5. Add tests and documentation

### Extending Lineage Tracking

1. Identify new data sources or transformations
2. Add OpenLineage event emission points
3. Update lineage queries and examples
4. Test with end-to-end workflow

## 🚦 Service Management

### Start Services

```bash
./scripts/setup/start-phase1.sh
```

### Stop Services

```bash
./scripts/setup/stop-phase1.sh
```

### View Logs

```bash
docker-compose logs -f [service-name]
```

### Check Service Health

```bash
docker-compose ps
```

## 🔍 Monitoring and Troubleshooting

### Health Checks

All services include health checks:
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- MinIO: HTTP health endpoint
- Services: Custom health endpoints

### Common Issues

1. **Port Conflicts**: Ensure ports 5000, 8080, 8081, 8888, 9000, 9001 are available
2. **Docker Issues**: Ensure Docker is running and has sufficient resources
3. **Service Dependencies**: Services start in dependency order with health checks

### Logs

View logs for specific services:
```bash
docker-compose logs mlflow
docker-compose logs postgres
docker-compose logs redis
```

## 🗺️ Roadmap

### Phase 2 (Future)

- [ ] Marquez integration for centralized lineage
- [ ] Advanced authentication with real OAuth providers
- [ ] Production-ready model serving
- [ ] Comprehensive monitoring and alerting
- [ ] CI/CD integration
- [ ] Horizontal scaling support

### Advanced Features

- [ ] Interactive lineage visualization
- [ ] Natural language queries
- [ ] Mobile-friendly interfaces
- [ ] Advanced analytics and impact scoring
- [ ] Machine learning on lineage data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🆘 Support

For questions and support:

- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation
- Consult the OpenLineage documentation

## 🙏 Acknowledgments

- [OpenLineage](https://openlineage.io/) - Data lineage specification
- [Marquez](https://marquezproject.github.io/marquez/) - OpenLineage backend
- [MLflow](https://mlflow.org/) - ML lifecycle management
- [Feast](https://feast.dev/) - Feature store
- [Docker](https://www.docker.com/) - Containerization platform
