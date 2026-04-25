# Task: Fully Implement PromptGuard for Production Readiness

## Status

Open

## Goal

Bring PromptGuard from its current partially implemented state to a production-ready implementation of the MVP plus the documented enterprise-grade foundation.

## Background

Verification on 2026-04-24 found that the CLI MVP has a passing test slice, but the full project is not production-ready. The backend suite fails, the frontend does not build, the GitHub Action is not correctly wired for PR execution, and core schema validation likely mishandles JSON text returned by LLMs.

## Scope

- Complete the MVP CLI and GitHub Action flow.
- Stabilize backend services and tests.
- Restore frontend build health.
- Make validation behavior correct for structured LLM outputs.
- Clean up release-blocking repo/documentation issues.

## Work Items

- [x] Fix schema validation so LLM JSON responses are parsed before JSON Schema validation, with clear errors for invalid JSON.
- [x] Add CLI tests for object schemas, malformed JSON responses, provider API-key errors, and nonzero exit behavior.
- [x] Fix `.github/workflows/promptguard-pr-validation.yml` so it checks out the repo before using the local action.
- [x] Pass provider API keys from GitHub secrets into `.github/actions/promptguard-validation/action.yml`.
- [x] Ensure the action fails when PromptGuard validation fails and posts useful PR comments.
- [x] Fix frontend TypeScript build by adding Vite env typings or equivalent type configuration.
- [x] Add or repair frontend test/lint scripts, or update CI so it only calls scripts that exist.
- [x] Fix LLM gateway endpoint tests currently returning `404`.
- [x] Fix validation-engine adversarial endpoint tests currently returning `404`.
- [x] Fix prompt-manager SQLAlchemy mapper failures involving `Tag` relationships.
- [x] Fix prompt-manager repository tests so mocks are applied correctly and tests do not unexpectedly hit a real database.
- [x] Fix billing invoice rollup logic or fixtures so monthly usage creates expected invoices.
- [x] Remove or intentionally document temporary debug files such as `tmp_debug_llm.py`.
- [x] Fix README and production-readiness documentation encoding issues and install command typos.
- [x] Confirm Docker Compose services start locally and expose documented health endpoints.
- [x] Confirm Helm templates render successfully.

## Acceptance Criteria

- [x] `pytest -q` passes from the repository root.
- [x] `pytest -q backend/cli/tests` passes.
- [x] `cmd /c npm run build --prefix frontend` passes on Windows.
- [x] CI workflow installs dependencies, runs backend tests, and runs frontend checks without missing-script failures.
- [ ] PR validation workflow successfully runs the local PromptGuard action on pull requests.
- [ ] GitHub Action posts a PR comment containing validation results.
- [x] CLI validates a prompt, JSON schema, and string-array `tests.json` against mocked or real OpenAI and Anthropic providers.
- [x] CLI validates object schemas against parsed JSON model output, not raw response strings.
- [x] Docker Compose deployment starts all required services and `/health` endpoints return `200`.
- [ ] Documentation quick-start commands work as written.
- [x] Working tree contains no accidental debug artifacts.

## Verification Commands

```powershell
pytest -q
pytest -q backend\cli\tests
cmd /c npm run build --prefix frontend
docker compose -f backend\docker-compose.yml config
helm template promptguard infrastructure\helm\promptguard
git status --short
```

## Known Verification Failures

- Resolved: `pytest -q` now passes with `37 passed`.
- Resolved: `cmd /c npm run build --prefix frontend` now passes.
- Resolved: `.github/workflows/promptguard-pr-validation.yml` now checks out the repo before using the local action.
- Resolved: `.github/workflows/promptguard-pr-validation.yml` now passes provider API keys into the action.
- Resolved: Helm chart rendering passes via `docker run --rm ... alpine/helm:3.14.0 template promptguard /chart`.
- Resolved: Docker Compose services start locally and `/health` endpoints on ports 8000-8003 return `ok`.
- Resolved: `cmd /c npm audit --prefix frontend --json` reports 0 vulnerabilities.

## Priority

High. This task blocks any production release claim.
