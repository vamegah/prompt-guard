import asyncio
import json
import time
from typing import Any, Dict

import httpx
from prometheus_client import Counter, Histogram
from redis.asyncio import Redis

from app.core.config import settings
from app.core.audit import log_audit
from app.core.http import build_http_client
from app.schemas.job import ValidationJob
from promptguard_shared.models.prompt import PromptTemplate
from promptguard_shared.models.test import TestInput
from promptguard_shared.validation.schema_validator import SchemaValidator
from promptguard_shared.validation.advanced import (
    semantic_similarity,
    toxicity_hits,
    hallucination_hits,
)


async def process_job(job_data: Dict[str, Any]) -> Dict[str, Any]:
    job = ValidationJob(**job_data)
    prompt_template = PromptTemplate(name="job", template=job.prompt_template)
    validator = SchemaValidator(job.json_schema)

    total_passed = 0
    total_failed = 0
    semantic_failed = 0
    toxicity_hit_count = 0
    hallucination_hit_count = 0
    start = time.time()

    async with build_http_client(settings.llm_timeout_seconds) as client:
        for item in job.test_inputs:
            input_data = item.get("input_data", item)
            test_input = TestInput(input_data=input_data)
            prompt = prompt_template.render(**test_input.input_data)
            payload = {
                "provider": job.provider,
                "prompt": prompt,
                "model": job.model,
                "temperature": job.temperature,
                "max_tokens": job.max_tokens,
            }
            headers = (
                {"X-Internal-Key": settings.internal_api_key}
                if settings.internal_api_key
                else None
            )
            response = await client.post(
                settings.llm_gateway_url, json=payload, headers=headers
            )
            response.raise_for_status()
            llm_text = response.json()["text"]
            result = validator.validate(llm_text)
            errors = []
            if job.enable_semantic and "expected_output" in item:
                score = semantic_similarity(str(item["expected_output"]), llm_text)
                if score < job.semantic_threshold:
                    semantic_failed += 1
                    errors.append(f"semantic_similarity_below_threshold:{score:.3f}")
            if job.enable_toxicity and job.toxicity_terms:
                hits = toxicity_hits(llm_text, job.toxicity_terms)
                if hits:
                    toxicity_hit_count += len(hits)
                    errors.append(f"toxicity_hits:{','.join(hits)}")
            if job.enable_hallucination:
                allowed_sources = item.get("allowed_sources")
                hits = hallucination_hits(llm_text, allowed_sources)
                if hits:
                    hallucination_hit_count += len(hits)
                    errors.append(f"hallucination_hits:{','.join(hits)}")

            if result.passed:
                total_passed += 1
            else:
                total_failed += 1
            if errors:
                total_failed += 1
                if result.passed:
                    total_passed -= 1

    duration_sec = time.time() - start
    JOB_DURATION.observe(duration_sec)
    duration_ms = duration_sec * 1000
    return {
        "test_case_id": job.test_case_id,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "duration_ms": duration_ms,
        "provider": job.provider,
        "model": job.model or "",
        "semantic_failed": semantic_failed,
        "toxicity_hits": toxicity_hit_count,
        "hallucination_hits": hallucination_hit_count,
    }


async def run_worker() -> None:
    redis_client = Redis.from_url(settings.redis_url)
    while True:
        raw = await redis_client.brpoplpush(
            settings.queue_name, settings.processing_queue_name, timeout=5
        )
        if not raw:
            await asyncio.sleep(0.1)
            continue

        job_payload = raw.decode("utf-8")
        try:
            job_data = json.loads(job_payload)
        except json.JSONDecodeError:
            await redis_client.lrem(settings.processing_queue_name, 1, raw)
            continue

        retry_count = int(job_data.get("_retry", 0))
        try:
            result = await process_job(job_data)
            async with build_http_client(settings.analytics_timeout_seconds) as client:
                headers = (
                    {"X-Internal-Key": settings.internal_api_key}
                    if settings.internal_api_key
                    else None
                )
                response = await client.post(
                    settings.analytics_url, json=result, headers=headers
                )
                response.raise_for_status()
            await redis_client.lrem(settings.processing_queue_name, 1, raw)
            JOB_COUNTER.labels("success").inc()
            await log_audit(
                "system",
                "validation_complete",
                "validation_job",
                resource_id=str(result.get("test_case_id")),
                metadata={"total_failed": result.get("total_failed"), "total_passed": result.get("total_passed")},
            )
        except Exception as exc:
            await redis_client.lrem(settings.processing_queue_name, 1, raw)
            retry_count += 1
            job_data["_retry"] = retry_count
            job_data["_last_error"] = str(exc)[:500]
            if retry_count <= settings.max_retries:
                JOB_COUNTER.labels("retry").inc()
                await log_audit(
                    "system",
                    "validation_retry",
                    "validation_job",
                    resource_id=str(job_data.get("test_case_id")),
                    metadata={"retry": retry_count, "error": str(exc)[:200]},
                )
                backoff = min(
                    settings.retry_backoff_base_seconds * (2 ** (retry_count - 1)),
                    settings.retry_backoff_max_seconds,
                )
                await asyncio.sleep(backoff)
                await redis_client.rpush(
                    settings.queue_name, json.dumps(job_data)
                )
            else:
                JOB_COUNTER.labels("failed").inc()
                await log_audit(
                    "system",
                    "validation_failed",
                    "validation_job",
                    resource_id=str(job_data.get("test_case_id")),
                    metadata={"error": str(exc)[:200]},
                )
                await redis_client.rpush(
                    settings.dlq_queue_name, json.dumps(job_data)
                )


if __name__ == "__main__":
    asyncio.run(run_worker())
JOB_COUNTER = Counter(
    "validation_jobs_total",
    "Total validation jobs processed",
    ["status"],
)
JOB_DURATION = Histogram(
    "validation_job_duration_seconds",
    "Validation job duration in seconds",
)
