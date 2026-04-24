#!/bin/bash

echo "Setting up PromptGuard development environment..."

# Create Python virtual environment
cd backend/cli
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Install frontend dependencies
cd ../../frontend
npm install

# Copy environment files
cd ../backend
cp .env.example .env

echo "Setup complete! Run 'docker-compose up' to start services."
