# Deployment guide

This guide covers runnable configurations for Compose, Helm, Terraform, monitoring, and smoke tests.

## Docker Compose (self-hosted)

Production-like stack:

```bash
cd backend
docker compose -f docker-compose.prod.yml up -d --build
```

Optional monitoring:

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.monitoring.yml up -d
```

Smoke test:

```powershell
./scripts/smoke/compose-smoke.ps1
```

## Air-gapped Compose

Preload images into a local registry, then:

```bash
cd backend
docker compose -f docker-compose.airgap.yml up -d
```

Smoke test:

```powershell
./scripts/smoke/compose-airgap-smoke.ps1
```

## Helm (Kubernetes)

Install the chart directly:

```bash
helm upgrade --install promptguard infrastructure/helm/promptguard \
  --namespace promptguard --create-namespace
```

Air-gapped override:

```bash
helm upgrade --install promptguard infrastructure/helm/promptguard \
  --namespace promptguard --create-namespace \
  -f infrastructure/helm/promptguard/values.airgap.yaml
```

Smoke test:

```bash
./scripts/smoke/helm-smoke.sh promptguard promptguard
```

## Terraform (Kubernetes)

```bash
cd infrastructure/terraform
terraform init
terraform apply -auto-approve
```

## Zero-downtime considerations

The Helm chart includes:
- RollingUpdate with `maxUnavailable: 0`
- PodDisruptionBudgets for API services
- Readiness/liveness probes on `/health`

## Database migrations

In production, run Alembic migrations. The API server no longer auto-creates tables unless `AUTO_CREATE_TABLES=true`.

## Monitoring

The Compose monitoring stack exposes:
- Prometheus at `http://localhost:9090`
- Grafana at `http://localhost:3001` (admin password via `GRAFANA_ADMIN_PASSWORD`)
- Alertmanager at `http://localhost:9093`

Alert routing is configured in `infrastructure/monitoring/alertmanager.yml`.

## Backups and retention

Automated backups in production Compose are enabled via the `backup` service. Configure:
- `BACKUP_S3_BUCKET` for off-host storage.
- `BACKUP_VERIFY_RESTORE=true` to verify backups on each run.

See `docs/runbooks/operations.md` for backup/restore steps and retention policy.

## Internal mTLS

The services support optional client TLS configuration for internal HTTP calls. Set:
- `INTERNAL_CA_BUNDLE` to a CA bundle path
- `INTERNAL_CLIENT_CERT` and `INTERNAL_CLIENT_KEY` for mutual TLS

## Secrets management (Vault/KMS)

Prompt Manager supports multiple secret backends for encrypting stored LLM API keys:

- `SECRET_BACKEND=fernet` (default): uses `MASTER_KEY` (Fernet).
- `SECRET_BACKEND=vault`: uses Vault Transit.
- `SECRET_BACKEND=aws_kms`: uses AWS KMS for envelope encryption.

Vault Transit env vars:
- `VAULT_ADDR`, `VAULT_TOKEN`
- `VAULT_TRANSIT_MOUNT` (default `transit`)
- `VAULT_TRANSIT_KEY`
- `VAULT_NAMESPACE` (optional)

AWS KMS env vars:
- `AWS_REGION`
- `AWS_KMS_KEY_ID`
- `AWS_KMS_ENCRYPTION_CONTEXT` (JSON string, optional)

Rotation workflow:
1. Rotate the backend key (Vault Transit supports `/keys/<key>/rotate`).
2. Rewrap stored API keys:
   - `POST /api/v1/admin/api-keys/rewrap` (optionally pass `org_id`).
