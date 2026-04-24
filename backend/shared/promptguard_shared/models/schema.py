from pydantic import BaseModel
from typing import Dict, Any, Optional


class ValidationSchema(BaseModel):
    """JSON Schema for validating LLM responses."""

    id: Optional[str] = None
    name: str
    schema_dict: Dict[str, Any]  # The actual JSON schema
    description: Optional[str] = None
