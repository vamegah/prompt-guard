#!/bin/bash
set -e

echo "Running tests..."

# Backend shared
cd backend/shared
pytest
cd ..

# CLI
cd cli
pytest
cd ..

# Services (if tests exist)
for service in services/*; do
    if [ -d "$service/tests" ]; then
        echo "Testing $service"
        cd "$service"
        pytest
        cd ../..
    fi
done

# Frontend
cd frontend
npm test
cd ..

echo "All tests passed!"