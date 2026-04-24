import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.config import settings
from app.core.secrets import rotate_backend_key, rewrap_value, SecretsError
from app.core.audit import log_action
from app.db.session import AsyncSessionLocal
from app.models import LLMApiKey
from prometheus_client import Gauge, Counter


ROTATION_LAST_SUCCESS = Gauge(
    "promptguard_secret_rotation_last_success_timestamp",
    "Unix timestamp of last successful secret rotation/rewrap",
)
ROTATION_FAILURES = Counter(
    "promptguard_secret_rotation_failures_total",
    "Total secret rotation/rewrap failures",
)


async def run_secret_rotation_once() -> dict:
    async with AsyncSessionLocal() as session:
        try:
            rotate_backend_key()
        except SecretsError:
            pass
        try:
            result = await session.execute(select(LLMApiKey))
            rows = result.scalars().all()
            for row in rows:
                row.encrypted_value = rewrap_value(row.encrypted_value)
            await session.commit()
            await log_action(
                session,
                "system",
                "rotate_rewrap",
                "api_key",
                datetime.now(timezone.utc).isoformat(),
                metadata={"rewrapped": len(rows)},
            )
            ROTATION_LAST_SUCCESS.set(datetime.now(timezone.utc).timestamp())
            return {"rewrapped": len(rows)}
        except Exception:
            ROTATION_FAILURES.inc()
            raise


async def rotation_loop(stop_event: asyncio.Event) -> None:
    interval = max(1, settings.SECRET_ROTATION_INTERVAL_HOURS)
    while not stop_event.is_set():
        await run_secret_rotation_once()
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval * 3600)
        except asyncio.TimeoutError:
            continue
