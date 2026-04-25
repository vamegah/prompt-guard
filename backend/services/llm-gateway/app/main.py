import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import Response
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from redis.asyncio import Redis

from app.clients.registry import Provider, get_client_factory
from app.core.cache import build_cache_key, get_cached_text, set_cached_text
from app.core.config import settings
from app.core.security import verify_internal_key
from app.core.audit import log_audit
from app.core.http import build_http_client
from app.schemas.llm import LLMGenerateRequest, LLMGenerateResponse


redis_client: Redis | None = None
if "llm_gateway_requests_total" in REGISTRY._names_to_collectors:
    REQUEST_COUNTER = REGISTRY._names_to_collectors["llm_gateway_requests_total"]
else:
    REQUEST_COUNTER = Counter(
        "llm_gateway_requests_total",
        "Total LLM gateway requests",
        ["provider", "status"],
    )
if "llm_gateway_request_latency_seconds" in REGISTRY._names_to_collectors:
    REQUEST_LATENCY = REGISTRY._names_to_collectors["llm_gateway_request_latency_seconds"]
else:
    REQUEST_LATENCY = Histogram(
        "llm_gateway_request_latency_seconds",
        "LLM gateway request latency in seconds",
        ["provider"],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    if settings.environment.lower() == "production":
        if not settings.require_org_scoped_keys:
            raise RuntimeError("REQUIRE_ORG_SCOPED_KEYS must be true in production")
        if not settings.prompt_manager_url or not settings.prompt_manager_internal_key:
            raise RuntimeError("PROMPT_MANAGER_URL and PROMPT_MANAGER_INTERNAL_KEY must be set in production")
    redis_client = Redis.from_url(settings.redis_url)
    yield
    if redis_client:
        await redis_client.aclose()
        redis_client = None


app = FastAPI(title="LLM Gateway", version="0.1.0", lifespan=lifespan)


def _resolve_api_key(provider: Provider) -> str | None:
    if provider == Provider.openai:
        return settings.openai_api_key
    if provider == Provider.anthropic:
        return settings.anthropic_api_key
    return None


async def _fetch_org_api_key(org_id: str, provider: Provider) -> str | None:
    if not settings.prompt_manager_url or not settings.prompt_manager_internal_key:
        return None
    url = f"{settings.prompt_manager_url.rstrip('/')}/api/v1/internal/orgs/{org_id}/api-keys/{provider.value}"
    async with build_http_client(3) as client:
        resp = await client.get(
            url,
            headers={"X-Internal-Key": settings.prompt_manager_internal_key},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        payload = resp.json()
        return payload.get("value")


@app.post(
    "/api/v1/generate",
    response_model=LLMGenerateResponse,
    dependencies=[Depends(verify_internal_key)],
)
async def generate(
    req: LLMGenerateRequest,
    x_org_id: str | None = Header(default=None, alias="X-Org-Id"),
) -> LLMGenerateResponse:
    actor = x_org_id or "system"
    try:
        provider = Provider(req.provider)
    except Exception:
        await log_audit(actor, "generate_failed", "llm_request", metadata={"reason": "unsupported_provider"})
        raise HTTPException(status_code=400, detail="Unsupported provider")

    model = req.model or settings.default_models.get(provider.value)
    if not model:
        await log_audit(actor, "generate_failed", "llm_request", metadata={"reason": "missing_model"})
        raise HTTPException(status_code=400, detail="Model not specified")

    api_key = None
    enforce_org_keys = (
        settings.environment.lower() == "production" and settings.require_org_scoped_keys
    )
    if enforce_org_keys and not x_org_id:
        await log_audit(actor, "generate_failed", "llm_request", metadata={"reason": "missing_org_id"})
        raise HTTPException(status_code=400, detail="Missing org id for key resolution")
    if not enforce_org_keys:
        api_key = _resolve_api_key(provider)
    if not api_key and x_org_id:
        api_key = await _fetch_org_api_key(x_org_id, provider)
    if not api_key:
        await log_audit(actor, "generate_failed", "llm_request", metadata={"reason": "missing_provider_key"})
        raise HTTPException(status_code=400, detail="Missing provider API key")

    cached = False
    cache_key = None
    if req.cache and redis_client:
        cache_key = req.cache_key or build_cache_key(
            settings.cache_namespace, provider.value, model, req.prompt
        )
        cached_text = await get_cached_text(redis_client, cache_key)
        if cached_text is not None:
            await log_audit(actor, "generate_cached", "llm_request", metadata={"provider": provider.value, "model": model})
            return LLMGenerateResponse(
                text=cached_text,
                provider=provider.value,
                model=model,
                cost_cents=0.0,
                latency_ms=0.0,
                cached=True,
            )

    client_factory = get_client_factory(provider)
    client = client_factory(api_key, model)

    start = time.time()
    status = "success"
    try:
        text = await client.generate(
            req.prompt, temperature=req.temperature, max_tokens=req.max_tokens
        )
    except Exception:
        status = "error"
        REQUEST_COUNTER.labels(provider.value, status).inc()
        raise
    finally:
        elapsed = time.time() - start
        REQUEST_LATENCY.labels(provider.value).observe(elapsed)
    latency_ms = elapsed * 1000

    if req.cache and redis_client and cache_key:
        await set_cached_text(redis_client, cache_key, text, settings.cache_ttl_seconds)

    REQUEST_COUNTER.labels(provider.value, status).inc()
    response = LLMGenerateResponse(
        text=text,
        provider=provider.value,
        model=model,
        cost_cents=0.0,
        latency_ms=latency_ms,
        cached=cached,
    )
    await log_audit(
        actor,
        "generate",
        "llm_request",
        metadata={"provider": provider.value, "model": model, "cached": cached},
    )
    if settings.billing_url and x_org_id:
        try:
            async with build_http_client(2) as client:
                await client.post(
                    settings.billing_url,
                    json={
                        "org_id": x_org_id,
                        "event_type": "llm_call",
                        "units": 1,
                        "cost_cents": 0,
                        "metadata": {"provider": provider.value, "model": model},
                    },
                    headers=(
                        {"X-API-Key": settings.billing_api_key}
                        if settings.billing_api_key
                        else None
                    ),
                )
        except Exception:
            pass
    return response


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
