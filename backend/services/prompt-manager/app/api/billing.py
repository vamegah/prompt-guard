from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.core.security import verify_api_key, role_required
from app.core.audit import log_action
from app.db.session import get_db
from app.models import Plan, Subscription, UsageEvent


router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/plans", dependencies=[Depends(role_required("admin"))])
async def create_plan(
    name: str,
    monthly_price_cents: int = 0,
    included_validation_runs: int = 0,
    included_llm_calls: int = 0,
    db: AsyncSession = Depends(get_db),
):
    plan = Plan(
        name=name,
        monthly_price_cents=monthly_price_cents,
        included_validation_runs=included_validation_runs,
        included_llm_calls=included_llm_calls,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return {"id": plan.id, "name": plan.name}


@router.get("/plans", response_model=List[dict])
async def list_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Plan))
    plans = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "monthly_price_cents": p.monthly_price_cents,
            "included_validation_runs": p.included_validation_runs,
            "included_llm_calls": p.included_llm_calls,
        }
        for p in plans
    ]


@router.post("/subscriptions", dependencies=[Depends(role_required("admin"))])
async def create_subscription(
    org_id: UUID,
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    subscription = Subscription(org_id=org_id, plan_id=plan_id)
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    await log_action(db, x_actor or "system", "create", "subscription", str(subscription.id))
    return {"id": subscription.id}


@router.post("/usage", dependencies=[Depends(role_required("admin"))])
async def record_usage(
    org_id: UUID,
    event_type: str,
    units: int = 1,
    cost_cents: int = 0,
    metadata: dict | None = None,
    db: AsyncSession = Depends(get_db),
):
    event = UsageEvent(
        org_id=org_id,
        event_type=event_type,
        units=units,
        cost_cents=cost_cents,
        metadata=metadata or {},
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return {"id": event.id}


@router.get("/usage/summary", response_model=dict, dependencies=[Depends(role_required("admin"))])
async def usage_summary(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            func.coalesce(func.sum(UsageEvent.units), 0),
            func.coalesce(func.sum(UsageEvent.cost_cents), 0),
        ).where(UsageEvent.org_id == org_id)
    )
    total_units, total_cost = result.one()
    return {"org_id": org_id, "total_units": total_units, "total_cost_cents": total_cost}
