from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.core.security import verify_api_key, require_role
from app.core.oidc import Principal, get_current_principal
from app.core.limiter import limiter
from app.core.audit import log_action
from app.models import TestSuite, Prompt, Schema
from app.schemas import TestSuiteCreate, TestSuiteUpdate, TestSuiteInDB, TestInput

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/", response_model=TestSuiteInDB, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_test_suite(
    request: Request,
    test_suite: TestSuiteCreate,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    await require_role("editor", principal, db)
    # Resolve prompt and schema IDs to ensure they exist (optional)
    # For simplicity, we'll just store the IDs; we can validate existence.
    data = test_suite.model_dump()
    prompt_ids = data.pop("prompt_ids", [])
    schema_ids = data.pop("schema_ids", [])
    db_test_suite = TestSuite(**data, org_id=principal.org_id)
    # Load related objects
    if prompt_ids:
        result = await db.execute(
            select(Prompt)
            .where(Prompt.id.in_(prompt_ids))
            .where(Prompt.org_id == principal.org_id)
        )
        prompts = result.scalars().all()
        if len(prompts) != len(prompt_ids):
            raise HTTPException(status_code=404, detail="Prompt not found")
        db_test_suite.prompts = prompts
    if schema_ids:
        result = await db.execute(
            select(Schema)
            .where(Schema.id.in_(schema_ids))
            .where(Schema.org_id == principal.org_id)
        )
        schemas = result.scalars().all()
        if len(schemas) != len(schema_ids):
            raise HTTPException(status_code=404, detail="Schema not found")
        db_test_suite.schemas = schemas
    db.add(db_test_suite)
    await db.commit()
    await db.refresh(db_test_suite)
    await log_action(
        db, x_actor or "system", "create", "test_suite", str(db_test_suite.id)
    )
    return db_test_suite


@router.get("/", response_model=List[TestSuiteInDB])
@limiter.limit("60/minute")
async def list_test_suites(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    await require_role("viewer", principal, db)
    result = await db.execute(
        select(TestSuite)
        .options(selectinload(TestSuite.prompts), selectinload(TestSuite.schemas))
        .where(TestSuite.org_id == principal.org_id)
        .offset(skip)
        .limit(limit)
    )
    test_suites = result.scalars().all()
    return test_suites


@router.get("/{test_suite_id}", response_model=TestSuiteInDB)
@limiter.limit("60/minute")
async def get_test_suite(
    request: Request,
    test_suite_id: UUID,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    await require_role("viewer", principal, db)
    result = await db.execute(
        select(TestSuite)
        .options(selectinload(TestSuite.prompts), selectinload(TestSuite.schemas))
        .where(TestSuite.id == test_suite_id)
        .where(TestSuite.org_id == principal.org_id)
    )
    test_suite = result.scalar_one_or_none()
    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return test_suite


@router.patch("/{test_suite_id}", response_model=TestSuiteInDB)
@limiter.limit("20/minute")
async def update_test_suite(
    request: Request,
    test_suite_id: UUID,
    test_suite_update: TestSuiteUpdate,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    await require_role("editor", principal, db)
    result = await db.execute(
        select(TestSuite)
        .options(selectinload(TestSuite.prompts), selectinload(TestSuite.schemas))
        .where(TestSuite.id == test_suite_id)
        .where(TestSuite.org_id == principal.org_id)
    )
    test_suite = result.scalar_one_or_none()
    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    update_data = test_suite_update.model_dump(exclude_unset=True)
    # Handle many-to-many updates
    if "prompt_ids" in update_data:
        prompt_ids = update_data.pop("prompt_ids")
        if prompt_ids is not None:
            result = await db.execute(
                select(Prompt)
                .where(Prompt.id.in_(prompt_ids))
                .where(Prompt.org_id == principal.org_id)
            )
            prompts = result.scalars().all()
            if len(prompts) != len(prompt_ids):
                raise HTTPException(status_code=404, detail="Prompt not found")
            test_suite.prompts = prompts
    if "schema_ids" in update_data:
        schema_ids = update_data.pop("schema_ids")
        if schema_ids is not None:
            result = await db.execute(
                select(Schema)
                .where(Schema.id.in_(schema_ids))
                .where(Schema.org_id == principal.org_id)
            )
            schemas = result.scalars().all()
            if len(schemas) != len(schema_ids):
                raise HTTPException(status_code=404, detail="Schema not found")
            test_suite.schemas = schemas
    for field, value in update_data.items():
        setattr(test_suite, field, value)
    await db.commit()
    await db.refresh(test_suite)
    await log_action(
        db, x_actor or "system", "update", "test_suite", str(test_suite.id)
    )
    return test_suite


@router.delete("/{test_suite_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_test_suite(
    request: Request,
    test_suite_id: UUID,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    await require_role("editor", principal, db)
    result = await db.execute(
        select(TestSuite)
        .where(TestSuite.id == test_suite_id)
        .where(TestSuite.org_id == principal.org_id)
    )
    test_suite = result.scalar_one_or_none()
    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    await db.delete(test_suite)
    await db.commit()
    await log_action(
        db, x_actor or "system", "delete", "test_suite", str(test_suite_id)
    )
    return None
