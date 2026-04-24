from pydantic import BaseModel
from typing import Any, Dict, Optional


class TestInput(BaseModel):
    """A single test input (values for placeholders)."""

    id: Optional[str] = None
    input_data: Dict[str, Any]  # e.g., {"input": "Hello world"}
    expected_output: Optional[Any] = None  # For semantic checks
    description: Optional[str] = None


class TestCase(BaseModel):
    """A complete test case combining prompt, schema, and inputs."""

    id: Optional[str] = None
    prompt_id: str
    schema_id: str
    inputs: list[TestInput]
    metadata: Dict[str, Any] = {}
