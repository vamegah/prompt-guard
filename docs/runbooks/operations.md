# Operations Runbook

## Backups (Postgres)

Automated backups (Compose prod):
- Backup container runs `pg_dump` on interval and optionally uploads to S3.
- Set `BACKUP_S3_BUCKET` for off-host storage.
- Set `BACKUP_VERIFY_RESTORE=true` to run a restore verification on each backup.

Manual (Compose/local):

```powershell
./scripts/ops/postgres_backup.ps1 -OutputPath ./backups
```

Restore:

```powershell
./scripts/ops/postgres_restore.ps1 -BackupFile ./backups/promptguard-YYYYMMDD-HHMMSS.sql
```

Retention policy:
- Keep daily backups for 30 days.
- Keep weekly backups for 12 weeks.
- Store backups off-host (object storage with versioning).

## Audit retention

Configuration (prompt-manager env):
- `AUDIT_RETENTION_ENABLED=true`
- `AUDIT_RETENTION_DAYS=90`
- `AUDIT_RETENTION_INTERVAL_HOURS=24`

The retention job deletes audit logs older than the configured window and writes an audit event.

## Secret rotation + rewrap

Configuration (prompt-manager env):
- `SECRET_ROTATION_ENABLED=true`
- `SECRET_ROTATION_INTERVAL_HOURS=24`

The rotation job:
1. Rotates the secret backend key if supported.
2. Rewraps all stored LLM API keys.
3. Writes an audit event with `rewrapped` count.

## SIEM export

Configuration (prompt-manager env):
- `SIEM_WEBHOOK_URL`
- `SIEM_API_KEY` (optional)

Audit events are POSTed to the SIEM webhook. Failures are non-blocking.

## Monitoring and alerts

Prometheus:
- `http://localhost:9090`

Alertmanager:
- `http://localhost:9093`

Alert routing:
- Update `infrastructure/monitoring/alertmanager.yml` to point at your SIEM webhook.
