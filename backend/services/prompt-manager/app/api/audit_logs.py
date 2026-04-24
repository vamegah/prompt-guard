from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import verify_api_key, role_required
from app.models import AuditLog


router = APIRouter(dependencies=[Depends(verify_api_key)])


class AuditIngest(BaseModel):
    actor: str
    action: str
    resource: str
    resource_id: str | None = None
    metadata: dict | None = None


@router.get("/", response_model=List[dict], dependencies=[Depends(role_required("admin"))])
async def list_audit_logs(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AuditLog).offset(skip).limit(limit))
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "actor": log.actor,
            "action": log.action,
            "resource": log.resource,
            "resource_id": log.resource_id,
            "metadata": log.meta,
            "created_at": log.created_at,
        }
        for log in logs
    ]


@router.post("/ingest", response_model=dict)
async def ingest_audit_log(payload: AuditIngest, db: AsyncSession = Depends(get_db)):
    if not payload.actor or not payload.action or not payload.resource:
        raise HTTPException(status_code=400, detail="Missing required fields")
    db_log = AuditLog(
        actor=payload.actor,
        action=payload.action,
        resource=payload.resource,
        resource_id=payload.resource_id,
        meta=payload.metadata or {},
    )
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return {"id": db_log.id}
