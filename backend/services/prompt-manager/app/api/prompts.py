from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.core.security import verify_api_key, require_role
from app.core.oidc import Principal, get_current_principal
from app.core.limiter import limiter
from app.core.audit import log_action
from app.models import Prompt
from app.schemas import PromptCreate, PromptUpdate, PromptInDB

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/", response_model=PromptInDB, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_prompt(
    request: Request,
    prompt: PromptCreate,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    await require_role("editor", principal, db)
    db_prompt = Prompt(**prompt.model_dump(), org_id=principal.org_id)
    db.add(db_prompt)
    await db.commit()
    await db.refresh(db_prompt)
    await log_action(
        db, x_actor or "system", "create", "prompt", str(db_prompt.id)
    )
    return db_prompt


@router.get("/", response_model=List[PromptInDB])
@limiter.limit("120/minute")
async def list_prompts(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    await require_role("viewer", principal, db)
    result = await db.execute(
        select(Prompt)
        .where(Prompt.org_id == principal.org_id)
        .offset(skip)
        .limit(limit)
    )
    prompts = result.scalars().all()
    return prompts


@router.get("/{prompt_id}", response_model=PromptInDB)
@limiter.limit("120/minute")
async def get_prompt(
    request: Request,
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    await require_role("viewer", principal, db)
    result = await db.execute(
        select(Prompt)
        .where(Prompt.id == prompt_id)
        .where(Prompt.org_id == principal.org_id)
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.patch("/{prompt_id}", response_model=PromptInDB)
@limiter.limit("30/minute")
async def update_prompt(
    request: Request,
    prompt_id: UUID,
    prompt_update: PromptUpdate,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    await require_role("editor", principal, db)
    result = await db.execute(
        select(Prompt)
        .where(Prompt.id == prompt_id)
        .where(Prompt.org_id == principal.org_id)
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    update_data = prompt_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prompt, field, value)
    await db.commit()
    await db.refresh(prompt)
    await log_action(db, x_actor or "system", "update", "prompt", str(prompt.id))
    return prompt


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_prompt(
    request: Request,
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    await require_role("editor", principal, db)
    result = await db.execute(
        select(Prompt)
        .where(Prompt.id == prompt_id)
        .where(Prompt.org_id == principal.org_id)
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    await db.delete(prompt)
    await db.commit()
    await log_action(db, x_actor or "system", "delete", "prompt", str(prompt_id))
    return None
