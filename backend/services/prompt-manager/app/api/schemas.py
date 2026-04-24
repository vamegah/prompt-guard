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
from app.models import Schema
from app.schemas import SchemaCreate, SchemaUpdate, SchemaInDB

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/", response_model=SchemaInDB, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_schema(
    request: Request,
    schema: SchemaCreate,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    await require_role("editor", principal, db)
    db_schema = Schema(**schema.model_dump(), org_id=principal.org_id)
    db.add(db_schema)
    await db.commit()
    await db.refresh(db_schema)
    await log_action(db, x_actor or "system", "create", "schema", str(db_schema.id))
    return db_schema


@router.get("/", response_model=List[SchemaInDB])
@limiter.limit("120/minute")
async def list_schemas(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    await require_role("viewer", principal, db)
    result = await db.execute(
        select(Schema)
        .where(Schema.org_id == principal.org_id)
        .offset(skip)
        .limit(limit)
    )
    schemas = result.scalars().all()
    return schemas


@router.get("/{schema_id}", response_model=SchemaInDB)
@limiter.limit("120/minute")
async def get_schema(
    request: Request,
    schema_id: UUID,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
):
    await require_role("viewer", principal, db)
    result = await db.execute(
        select(Schema)
        .where(Schema.id == schema_id)
        .where(Schema.org_id == principal.org_id)
    )
    schema = result.scalar_one_or_none()
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return schema


@router.patch("/{schema_id}", response_model=SchemaInDB)
@limiter.limit("30/minute")
async def update_schema(
    request: Request,
    schema_id: UUID,
    schema_update: SchemaUpdate,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    await require_role("editor", principal, db)
    result = await db.execute(
        select(Schema)
        .where(Schema.id == schema_id)
        .where(Schema.org_id == principal.org_id)
    )
    schema = result.scalar_one_or_none()
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    update_data = schema_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schema, field, value)
    await db.commit()
    await db.refresh(schema)
    await log_action(db, x_actor or "system", "update", "schema", str(schema.id))
    return schema


@router.delete("/{schema_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_schema(
    request: Request,
    schema_id: UUID,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    await require_role("editor", principal, db)
    result = await db.execute(
        select(Schema)
        .where(Schema.id == schema_id)
        .where(Schema.org_id == principal.org_id)
    )
    schema = result.scalar_one_or_none()
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    await db.delete(schema)
    await db.commit()
    await log_action(db, x_actor or "system", "delete", "schema", str(schema_id))
    return None
