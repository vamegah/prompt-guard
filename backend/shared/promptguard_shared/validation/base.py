from pydantic import BaseModel
from typing import List


class ValidationResult(BaseModel):
    """Result of a schema validation check."""

    passed: bool
    errors: List[str]
