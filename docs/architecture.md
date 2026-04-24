# PromptGuard Architecture

PromptGuard is a platform for validating LLM prompts against JSON schemas, designed for enterprise use.

## High-Level Components

- **CLI**: Developer tool for local validation and CI/CD integration.
- **Prompt Manager**: REST API for managing prompts, schemas, and test suites.
- **Validation Engine**: Async worker that runs validation jobs using LLMs.
- **LLM Gateway**: Proxy to multiple LLM providers with caching and cost tracking.
- **Analytics Service**: Collects and exposes metrics about validation runs.
- **Frontend Dashboard**: React-based UI for team collaboration.

## Data Flow

1. User creates a prompt, schema, and test suite via CLI or dashboard.
2. Validation job is submitted to Redis queue.
3. Validation Engine picks up job, calls LLM Gateway with test inputs.
4. LLM Gateway routes to appropriate provider, returns response.
5. Validation Engine validates response against schema, stores result.
6. Analytics service ingests metrics.
7. User views report in dashboard or CI.

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL, Redis
- **Frontend**: React, TypeScript, Vite, React Query
- **Infrastructure**: Docker, Kubernetes, Helm, Terraform (AWS)
- **Monitoring**: Prometheus, Grafana