from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.security import verify_api_key, role_required
from app.db.session import get_db
from app.models import Invoice
from app.jobs.invoice_rollup import create_invoice_rollups, month_bounds


router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/rollup", dependencies=[Depends(role_required("admin"))])
async def rollup_invoices(
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
):
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    start, end = month_bounds(start)
    count = await create_invoice_rollups(db, start, end)
    return {"created": count, "period_start": start, "period_end": end}


@router.get("/", response_model=List[dict], dependencies=[Depends(role_required("admin"))])
async def list_invoices(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Invoice).where(Invoice.org_id == org_id))
    invoices = result.scalars().all()
    return [
        {
            "id": i.id,
            "org_id": i.org_id,
            "period_start": i.period_start,
            "period_end": i.period_end,
            "total_units": i.total_units,
            "total_cost_cents": i.total_cost_cents,
        }
        for i in invoices
    ]
