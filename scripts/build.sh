#!/bin/bash
set -e

VERSION=${1:-latest}
REGISTRY=${2:-docker.io/promptguard}

echo "Building Docker images version $VERSION"

# Shared library first (if needed as base)
# For simplicity, we build each service assuming shared is included in Dockerfile

# Prompt Manager
docker build -t $REGISTRY/prompt-manager:$VERSION -f backend/services/prompt-manager/Dockerfile backend/

# Validation Engine
docker build -t $REGISTRY/validation-engine:$VERSION -f backend/services/validation-engine/Dockerfile backend/

# LLM Gateway
docker build -t $REGISTRY/llm-gateway:$VERSION -f backend/services/llm-gateway/Dockerfile backend/

# Analytics
docker build -t $REGISTRY/analytics:$VERSION -f backend/services/analytics/Dockerfile backend/

# Frontend
docker build -t $REGISTRY/frontend:$VERSION -f frontend/Dockerfile frontend/

echo "Images built successfully."