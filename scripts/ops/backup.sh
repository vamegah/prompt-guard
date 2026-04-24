#!/bin/sh
set -eu

INTERVAL_HOURS="${BACKUP_INTERVAL_HOURS:-24}"
PGHOST="${PGHOST:-postgres}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-promptguard}"
PGPASSWORD="${PGPASSWORD:-promptguard}"
PGDATABASE="${PGDATABASE:-promptguard}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
S3_BUCKET="${S3_BUCKET:-}"
VERIFY_RESTORE="${VERIFY_RESTORE:-false}"

mkdir -p "$BACKUP_DIR"

if command -v aws >/dev/null 2>&1; then
  : # aws cli available
else
  apk add --no-cache aws-cli >/dev/null 2>&1 || true
fi

export PGPASSWORD

while true; do
  TS="$(date -u +%Y%m%d-%H%M%S)"
  FILE="$BACKUP_DIR/promptguard-$TS.sql"
  pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE" > "$FILE"

  if [ "$VERIFY_RESTORE" = "true" ]; then
    TMP_DB="promptguard_verify_$TS"
    psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -c "CREATE DATABASE $TMP_DB;"
    psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$TMP_DB" < "$FILE"
    psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -c "DROP DATABASE $TMP_DB;"
  fi

  if [ -n "$S3_BUCKET" ]; then
    aws s3 cp "$FILE" "s3://$S3_BUCKET/$(basename "$FILE")"
  fi

  sleep "$((INTERVAL_HOURS * 3600))"
done
