from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


class PromptTestResult(BaseModel):
    """Result of a single test input validation."""

    test_input_id: str
    passed: bool
    errors: List[str] = Field(default_factory=list)
    llm_response: Optional[Any] = None
    llm_latency_ms: Optional[float] = None
    llm_cost: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ValidationReport(BaseModel):
    """Complete report for a test run."""

    test_case_id: str
    results: List[PromptTestResult]
    total_passed: int
    total_failed: int
    duration_ms: float
    metadata: Dict[str, Any] = {}
