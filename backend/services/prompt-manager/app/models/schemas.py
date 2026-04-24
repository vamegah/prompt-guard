from typing import List, Any
from uuid import UUID
import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.db.session import get_db
from app.repositories import SchemaRepository


# Pydantic Schemas for Schemas
class SchemaBase(BaseModel):
    name: str
    description: str | None = None
    json_schema: dict[str, Any]


class SchemaCreate(SchemaBase):
    pass


class SchemaUpdate(SchemaBase):
    name: str | None = None
    json_schema: dict[str, Any] | None = None


class SchemaResponse(SchemaBase):
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None

    model_config = ConfigDict(from_attributes=True)


router = APIRouter()


@router.post("/", response_model=SchemaResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_schema(
    request: Request, schema_in: SchemaCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new schema.
    """
    repo = SchemaRepository(db)
    schema = await repo.create(schema_in)
    return schema


@router.get("/{schema_id}", response_model=SchemaResponse)
async def get_schema(schema_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single schema by its ID.
    """
    repo = SchemaRepository(db)
    schema = await repo.get(schema_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schema not found"
        )
    return schema


@router.get("/", response_model=List[SchemaResponse])
async def get_all_schemas(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all schemas.
    """
    repo = SchemaRepository(db)
    schemas = await repo.get_all(skip=skip, limit=limit)
    return schemas


@router.put("/{schema_id}", response_model=SchemaResponse)
async def update_schema(
    schema_id: UUID,
    schema_in: SchemaUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing schema.
    """
    repo = SchemaRepository(db)
    db_schema = await repo.get(schema_id)
    if not db_schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schema not found"
        )
    updated_schema = await repo.update(db_schema, schema_in)
    return updated_schema


@router.delete("/{schema_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schema(
    schema_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a schema.
    """
    repo = SchemaRepository(db)
    db_schema = await repo.get(schema_id)
    if not db_schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schema not found"
        )
    await repo.delete(db_schema)
