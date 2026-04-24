from app.core.config import settings
from app.core.http import build_http_client


async def log_audit(
    actor: str,
    action: str,
    resource: str,
    resource_id: str | None = None,
    metadata: dict | None = None,
) -> None:
    if not settings.audit_url:
        return
    payload = {
        "actor": actor,
        "action": action,
        "resource": resource,
        "resource_id": resource_id,
        "metadata": metadata or {},
    }
    headers = (
        {"X-API-Key": settings.audit_api_key}
        if settings.audit_api_key
        else None
    )
    try:
        async with build_http_client(2) as client:
            await client.post(settings.audit_url, json=payload, headers=headers)
    except Exception:
        return
