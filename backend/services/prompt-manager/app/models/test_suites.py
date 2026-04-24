from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.test_suite import TestSuite
from app.repositories.test_suite import TestSuiteRepository

# Assuming you have Pydantic schemas for request/response bodies
# For simplicity, we'll define them inline for this example.
from pydantic import BaseModel, ConfigDict


class TestSuiteCreate(BaseModel):
    name: str
    description: str | None = None
    test_inputs: List[dict] = []


class TestSuiteUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    test_inputs: List[dict] | None = None


class TestSuiteResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    test_inputs: List[dict]
    # Add other fields like created_at, updated_at if needed

    model_config = ConfigDict(from_attributes=True)


router = APIRouter()


@router.post("/", response_model=TestSuiteResponse, status_code=status.HTTP_201_CREATED)
async def create_test_suite(
    test_suite_in: TestSuiteCreate, db: AsyncSession = Depends(get_db)
):
    repo = TestSuiteRepository(db)
    test_suite = await repo.create(test_suite_in)
    return test_suite


@router.get("/{test_suite_id}", response_model=TestSuiteResponse)
async def get_test_suite(test_suite_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = TestSuiteRepository(db)
    test_suite = await repo.get(test_suite_id)
    if not test_suite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test Suite not found"
        )
    return test_suite


@router.get("/", response_model=List[TestSuiteResponse])
async def get_all_test_suites(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    repo = TestSuiteRepository(db)
    test_suites = await repo.get_all(skip=skip, limit=limit)
    return test_suites
