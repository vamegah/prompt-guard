import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import Response
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST, Counter
from redis.asyncio import Redis

from app.core.config import settings
from app.core.security import verify_internal_key
from app.core.audit import log_audit
from app.schemas.job import ValidationJob
from app.schemas.adversarial import (
    AdversarialRequest,
    AdversarialResponse,
    AdversarialValidationRequest,
    AdversarialValidationResponse,
)
from promptguard_shared.testing.adversarial import generate_adversarial_inputs


redis_client: Redis | None = None
if "validation_enqueue_total" in REGISTRY._names_to_collectors:
    ENQUEUE_COUNTER = REGISTRY._names_to_collectors["validation_enqueue_total"]
else:
    ENQUEUE_COUNTER = Counter(
        "validation_enqueue_total",
        "Total validation jobs enqueued",
        ["type"],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = Redis.from_url(settings.redis_url)
    yield
    if redis_client:
        await redis_client.aclose()
        redis_client = None


app = FastAPI(title="Validation Engine", version="0.1.0", lifespan=lifespan)


@app.post("/api/v1/validate", dependencies=[Depends(verify_internal_key)])
async def enqueue_validation(job: ValidationJob) -> dict:
    payload = job.model_dump()
    if redis_client:
        await redis_client.rpush(settings.queue_name, json.dumps(payload))
    ENQUEUE_COUNTER.labels("standard").inc()
    await log_audit(
        "system",
        "enqueue_validation",
        "validation_job",
        resource_id=str(job.test_case_id),
    )
    return {"status": "queued", "test_case_id": job.test_case_id}


@app.post(
    "/api/v1/adversarial",
    response_model=AdversarialResponse,
    dependencies=[Depends(verify_internal_key)],
)
async def generate_adversarial(req: AdversarialRequest) -> AdversarialResponse:
    generated = generate_adversarial_inputs(req.base_inputs, req.count_per_input)
    ENQUEUE_COUNTER.labels("adversarial_generate").inc()
    await log_audit(
        "system",
        "generate_adversarial",
        "validation_job",
        metadata={"generated_count": len(generated)},
    )
    return AdversarialResponse(generated=generated)


@app.post(
    "/api/v1/adversarial/validate",
    response_model=AdversarialValidationResponse,
    dependencies=[Depends(verify_internal_key)],
)
async def generate_and_enqueue(req: AdversarialValidationRequest) -> AdversarialValidationResponse:
    generated = generate_adversarial_inputs(req.base_inputs, req.count_per_input)
    payload = {
        "test_case_id": req.test_case_id,
        "prompt_template": req.prompt_template,
        "json_schema": req.json_schema,
        "test_inputs": generated,
        "provider": req.provider,
        "model": req.model,
        "temperature": req.temperature,
        "max_tokens": req.max_tokens,
        "enable_semantic": req.enable_semantic,
        "semantic_threshold": req.semantic_threshold,
        "enable_toxicity": req.enable_toxicity,
        "toxicity_terms": req.toxicity_terms,
        "enable_hallucination": req.enable_hallucination,
    }
    if redis_client:
        await redis_client.rpush(settings.queue_name, json.dumps(payload))
    ENQUEUE_COUNTER.labels("adversarial_validate").inc()
    await log_audit(
        "system",
        "enqueue_adversarial_validation",
        "validation_job",
        resource_id=str(req.test_case_id),
        metadata={"generated_count": len(generated)},
    )
    return AdversarialValidationResponse(
        status="queued", test_case_id=req.test_case_id, generated_count=len(generated)
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
