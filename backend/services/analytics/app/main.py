import time
from fastapi import FastAPI, Depends
from fastapi.responses import Response
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from typing import List

from app.schemas.metrics import ValidationMetric
from app.core.audit import log_audit
from app.core.security import verify_internal_key


app = FastAPI(title="Analytics Service", version="0.1.0")
metrics_store: List[ValidationMetric] = []
if "analytics_ingest_total" in REGISTRY._names_to_collectors:
    INGEST_COUNTER = REGISTRY._names_to_collectors["analytics_ingest_total"]
else:
    INGEST_COUNTER = Counter(
        "analytics_ingest_total",
        "Total metrics ingested",
    )
if "analytics_summary_latency_seconds" in REGISTRY._names_to_collectors:
    SUMMARY_LATENCY = REGISTRY._names_to_collectors["analytics_summary_latency_seconds"]
else:
    SUMMARY_LATENCY = Histogram(
        "analytics_summary_latency_seconds",
        "Summary endpoint latency in seconds",
    )


@app.post("/api/v1/metrics", dependencies=[Depends(verify_internal_key)])
async def ingest_metric(metric: ValidationMetric) -> dict:
    metrics_store.append(metric)
    INGEST_COUNTER.inc()
    await log_audit(
        "system",
        "ingest_metric",
        "validation_metric",
        resource_id=str(metric.test_case_id),
    )
    return {"status": "ingested"}


@app.get("/api/v1/metrics", response_model=List[ValidationMetric], dependencies=[Depends(verify_internal_key)])
async def list_metrics() -> List[ValidationMetric]:
    await log_audit("system", "list_metrics", "validation_metric")
    return metrics_store


@app.get("/api/v1/summary", dependencies=[Depends(verify_internal_key)])
async def summary() -> dict:
    await log_audit("system", "summary_metrics", "validation_metric")
    start = time.time()
    total_runs = len(metrics_store)
    total_passed = sum(m.total_passed for m in metrics_store)
    total_failed = sum(m.total_failed for m in metrics_store)
    semantic_failed = sum(m.semantic_failed for m in metrics_store)
    toxicity_hits = sum(m.toxicity_hits for m in metrics_store)
    hallucination_hits = sum(m.hallucination_hits for m in metrics_store)
    avg_duration = (
        sum(m.duration_ms for m in metrics_store) / total_runs if total_runs else 0.0
    )
    SUMMARY_LATENCY.observe(time.time() - start)
    return {
        "total_runs": total_runs,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "semantic_failed": semantic_failed,
        "toxicity_hits": toxicity_hits,
        "hallucination_hits": hallucination_hits,
        "avg_duration_ms": avg_duration,
    }


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
