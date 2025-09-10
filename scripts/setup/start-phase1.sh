#!/bin/bash

# Phase 1 MLOps Platform Startup Script

echo "Starting Phase 1 MLOps Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp configs/phase1/.env.example .env
    echo "Please update the .env file with your configuration before running again."
    exit 1
fi

# Start the services
echo "Starting services with docker-compose..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 30

# Check service health
echo "Checking service health..."
docker-compose ps

echo ""
echo "Phase 1 MLOps Platform is starting up!"
echo ""
echo "Service URLs:"
echo "- MLflow UI: http://localhost:5000"
echo "- ModelCatalogue: http://localhost:8080"
echo "- API Gateway: http://localhost:8081"
echo "- Jupyter Notebook: http://localhost:8888"
echo "- MinIO Console: http://localhost:9001"
echo ""
echo "Default credentials:"
echo "- MinIO: minioadmin / minioadmin"
echo "- Jupyter: No token required"
echo ""
echo "To view logs: docker-compose logs -f [service-name]"
echo "To stop services: docker-compose down"
