import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.core.config import settings
from app.core.audit import log_action
from app.db.session import AsyncSessionLocal
from app.models import AuditLog
from prometheus_client import Gauge, Counter


RETENTION_LAST_SUCCESS = Gauge(
    "promptguard_audit_retention_last_success_timestamp",
    "Unix timestamp of last successful audit retention run",
)
RETENTION_FAILURES = Counter(
    "promptguard_audit_retention_failures_total",
    "Total audit retention failures",
)


async def run_audit_retention_once() -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.AUDIT_RETENTION_DAYS)
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                delete(AuditLog).where(AuditLog.created_at < cutoff)
            )
            await session.commit()
            deleted = result.rowcount or 0
            await log_action(
                session,
                "system",
                "audit_retention",
                "audit_log",
                cutoff.isoformat(),
                metadata={"deleted": deleted},
            )
            RETENTION_LAST_SUCCESS.set(datetime.now(timezone.utc).timestamp())
            return {"deleted": deleted}
        except Exception:
            RETENTION_FAILURES.inc()
            raise


async def retention_loop(stop_event: asyncio.Event) -> None:
    interval = max(1, settings.AUDIT_RETENTION_INTERVAL_HOURS)
    while not stop_event.is_set():
        await run_audit_retention_once()
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval * 3600)
        except asyncio.TimeoutError:
            continue
