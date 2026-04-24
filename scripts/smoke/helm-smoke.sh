#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-promptguard}"
RELEASE="${2:-promptguard}"

kubectl -n "${NAMESPACE}" rollout status deploy/"${RELEASE}"-promptguard-prompt-manager --timeout=180s
kubectl -n "${NAMESPACE}" rollout status deploy/"${RELEASE}"-promptguard-llm-gateway --timeout=180s
kubectl -n "${NAMESPACE}" rollout status deploy/"${RELEASE}"-promptguard-validation-api --timeout=180s
kubectl -n "${NAMESPACE}" rollout status deploy/"${RELEASE}"-promptguard-analytics --timeout=180s

echo "Helm smoke test passed."
