from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any


class TestInput(BaseModel):
    input_data: Dict[str, Any]
    expected_output: Optional[Any] = None
    description: Optional[str] = None


class TestSuiteBase(BaseModel):
    name: str
    description: Optional[str] = None
    prompt_ids: List[UUID] = Field(default_factory=list)
    schema_ids: List[UUID] = Field(default_factory=list)
    test_inputs: List[TestInput] = Field(default_factory=list)


class TestSuiteCreate(TestSuiteBase):
    pass


class TestSuiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt_ids: Optional[List[UUID]] = None
    schema_ids: Optional[List[UUID]] = None
    test_inputs: Optional[List[TestInput]] = None


class TestSuiteInDB(TestSuiteBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
