from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.security import verify_internal_key
from app.core.secrets import decrypt_value
from app.db.session import get_db
from app.models import LLMApiKey


router = APIRouter(dependencies=[Depends(verify_internal_key)])


@router.get("/orgs/{org_id}/api-keys/{provider}")
async def get_org_api_key(
    org_id: UUID,
    provider: str,
    name: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(LLMApiKey).where(
        LLMApiKey.org_id == org_id, LLMApiKey.provider == provider
    )
    if name:
        stmt = stmt.where(LLMApiKey.name == name)
    stmt = stmt.order_by(LLMApiKey.last_rotated_at.desc())
    result = await db.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise HTTPException(status_code=404, detail="API key not found")
    return {
        "id": entry.id,
        "provider": entry.provider,
        "name": entry.name,
        "value": decrypt_value(entry.encrypted_value),
    }
