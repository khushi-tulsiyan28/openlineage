# Repository Structure Overview

This document provides a detailed overview of the organized structure of the MLOps Platform with OpenLineage Integration repository.

## 📁 Directory Structure

```
openlineage/
├── 📄 README.md                           # Main repository documentation
├── 📄 STRUCTURE.md                        # This file - structure overview
├── 📄 requirements.txt                    # Python dependencies
├── 📄 .gitignore                          # Git ignore rules
├── 🐳 docker-compose.yml                  # Phase 1 Docker Compose configuration
│
├── 📚 docs/                               # Documentation
│   ├── 📄 PHASE1_IMPLEMENTATION_DOCUMENT.md  # Detailed Phase 1 implementation guide
│   ├── 🏗️ architecture/                   # Architecture documentation
│   │   ├── 📄 phase1-architecture.md     # Phase 1 architecture (simplified)
│   │   └── 📄 mlops-architecture.md      # Complete MLOps architecture
│   ├── ⚙️ setup/                          # Setup guides
│   │   └── 📄 MLOPS_SETUP.md             # Complete setup instructions
│   └── 🔄 workflows/                      # Workflow documentation
│       └── 📄 workflow_narrative.md      # End-to-end workflow description
│
├── ⚙️ configs/                            # Configuration files
│   ├── 📁 phase1/                         # Phase 1 configurations
│   │   └── 📄 .env.example               # Environment variables template
│   └── 📁 phase2/                         # Phase 2 configurations (future)
│
├── 🔌 integrations/                       # OpenLineage integrations
│   ├── 📁 mlflow/                         # MLflow integration
│   │   └── 🐍 mlflow_openlineage_integration.py
│   ├── 📁 feast/                          # Feast integration
│   │   └── 🐍 feast_openlineage_integration.py
│   └── 📁 modelcatalogue/                 # ModelCatalogue integration
│       └── 🐍 modelcatalogue_openlineage_integration.py
│
├── 📖 examples/                           # Example code
│   ├── 📁 basic/                          # Basic examples
│   │   └── 🐍 openlineage_queries.py     # Lineage query examples
│   └── 📁 advanced/                       # Advanced examples (future)
│
├── 🔄 workflows/                          # Workflow implementations
│   ├── 📁 phase1/                         # Phase 1 workflows
│   │   └── 🐍 end_to_end_workflow.py     # Complete MLOps workflow
│   └── 📁 phase2/                         # Phase 2 workflows (future)
│
└── 🛠️ scripts/                            # Utility scripts
    ├── 📁 setup/                          # Setup scripts
    │   ├── 🐚 start-phase1.sh            # Start Phase 1 platform
    │   └── 🐚 stop-phase1.sh             # Stop Phase 1 platform
    └── 📁 deployment/                     # Deployment scripts (future)
```

## 📋 File Descriptions

### Core Files
- **README.md**: Main repository documentation with quick start guide
- **docker-compose.yml**: Phase 1 Docker Compose configuration for all services
- **requirements.txt**: Python dependencies for the project
- **.gitignore**: Git ignore rules for Python, Docker, and development files

### Documentation (`docs/`)
- **PHASE1_IMPLEMENTATION_DOCUMENT.md**: Comprehensive guide to Phase 1 implementation
- **architecture/phase1-architecture.md**: Simplified architecture without OpenLineage
- **architecture/mlops-architecture.md**: Complete MLOps architecture with OpenLineage
- **setup/MLOPS_SETUP.md**: Detailed setup instructions for the full platform
- **workflows/workflow_narrative.md**: Step-by-step workflow description

### Configuration (`configs/`)
- **phase1/.env.example**: Environment variables template for Phase 1

### Integrations (`integrations/`)
- **mlflow/mlflow_openlineage_integration.py**: MLflow OpenLineage integration
- **feast/feast_openlineage_integration.py**: Feast OpenLineage integration
- **modelcatalogue/modelcatalogue_openlineage_integration.py**: ModelCatalogue OpenLineage integration

### Examples (`examples/`)
- **basic/openlineage_queries.py**: Examples of querying lineage information

### Workflows (`workflows/`)
- **phase1/end_to_end_workflow.py**: Complete MLOps workflow implementation

### Scripts (`scripts/`)
- **setup/start-phase1.sh**: Script to start the Phase 1 platform
- **setup/stop-phase1.sh**: Script to stop the Phase 1 platform

## 🎯 Key Features

### Phase 1 (Current)
- ✅ **Simplified Setup**: Single docker-compose file
- ✅ **Core Services**: MLflow, Feast, ModelCatalogue, API Gateway
- ✅ **Mock Services**: Fast prototyping without external dependencies
- ✅ **Health Checks**: Automatic service monitoring
- ✅ **Development Ready**: Easy local setup and testing

### Phase 2 (Future)
- 🔄 **Marquez Integration**: Centralized lineage backend
- 🔄 **Advanced Authentication**: Real OAuth providers
- 🔄 **Production Features**: Scaling, monitoring, CI/CD
- 🔄 **Enhanced Lineage**: Complete data lineage tracking

## 🚀 Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <repo-url>
   cd openlineage
   cp configs/phase1/.env.example .env
   ```

2. **Start Platform**:
   ```bash
   ./scripts/setup/start-phase1.sh
   ```

3. **Access Services**:
   - MLflow UI: http://localhost:5000
   - ModelCatalogue: http://localhost:8080
   - API Gateway: http://localhost:8081
   - Jupyter: http://localhost:8888

4. **Run Examples**:
   ```bash
   python workflows/phase1/end_to_end_workflow.py
   ```

## 📚 Documentation Navigation

- **Getting Started**: README.md
- **Architecture**: docs/architecture/
- **Setup**: docs/setup/
- **Workflows**: docs/workflows/
- **Implementation**: docs/PHASE1_IMPLEMENTATION_DOCUMENT.md
- **Examples**: examples/
- **Scripts**: scripts/

## 🔧 Development

### Adding New Features
1. Create feature branch
2. Add code to appropriate directory
3. Update documentation
4. Add tests
5. Submit pull request

### Directory Conventions
- **docs/**: All documentation files
- **configs/**: Configuration files by phase
- **integrations/**: Service-specific integrations
- **examples/**: Example code and tutorials
- **workflows/**: Workflow implementations
- **scripts/**: Utility and setup scripts

This structure provides a clear separation of concerns and makes it easy to navigate and extend the MLOps platform.
