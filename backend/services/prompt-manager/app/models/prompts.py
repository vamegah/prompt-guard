from typing import List, Any
from uuid import UUID
import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.prompt import PromptRepository


# Pydantic Schemas for Prompts, based on your api-spec.yaml
class PromptBase(BaseModel):
    name: str
    template: str
    description: str | None = None
    version: str = "1.0.0"
    metadata: dict[str, Any] | None = {}


class PromptCreate(PromptBase):
    pass


class PromptUpdate(PromptBase):
    name: str | None = None
    template: str | None = None


class PromptResponse(PromptBase):
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None

    model_config = ConfigDict(from_attributes=True)


router = APIRouter()


@router.post("/", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(prompt_in: PromptCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new prompt.
    """
    repo = PromptRepository(db)
    prompt = await repo.create(prompt_in)
    return prompt


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single prompt by its ID.
    """
    repo = PromptRepository(db)
    prompt = await repo.get(prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        )
    return prompt


@router.get("/", response_model=List[PromptResponse])
async def get_all_prompts(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all prompts.
    """
    repo = PromptRepository(db)
    prompts = await repo.get_all(skip=skip, limit=limit)
    return prompts


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: UUID,
    prompt_in: PromptUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing prompt.
    """
    repo = PromptRepository(db)
    db_prompt = await repo.get(prompt_id)
    if not db_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        )
    updated_prompt = await repo.update(db_prompt, prompt_in)
    return updated_prompt


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a prompt.
    """
    repo = PromptRepository(db)
    db_prompt = await repo.get(prompt_id)
    if not db_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        )
    await repo.delete(db_prompt)
