from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.core.config import settings
from app.models import AuditLog


async def log_action(
    db: AsyncSession,
    actor: str,
    action: str,
    resource: str,
    resource_id: str | None = None,
    metadata: dict | None = None,
) -> None:
    entry = AuditLog(
        actor=actor,
        action=action,
        resource=resource,
        resource_id=resource_id,
        metadata=metadata or {},
    )
    db.add(entry)
    await db.commit()
    if settings.SIEM_WEBHOOK_URL:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(
                    settings.SIEM_WEBHOOK_URL,
                    json={
                        "actor": actor,
                        "action": action,
                        "resource": resource,
                        "resource_id": resource_id,
                        "metadata": metadata or {},
                    },
                    headers=(
                        {"Authorization": f"Bearer {settings.SIEM_API_KEY}"}
                        if settings.SIEM_API_KEY
                        else None
                    ),
                )
        except Exception:
            pass
