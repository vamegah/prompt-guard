from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any


class SchemaBase(BaseModel):
    name: str
    json_schema: Dict[str, Any]
    description: Optional[str] = None


class SchemaCreate(SchemaBase):
    pass


class SchemaUpdate(BaseModel):
    name: Optional[str] = None
    json_schema: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class SchemaInDB(SchemaBase):
    id: UUID
    org_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
