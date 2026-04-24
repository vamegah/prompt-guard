from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class ValidationJob(BaseModel):
    test_case_id: str
    prompt_template: str
    json_schema: Dict[str, Any]
    test_inputs: List[Dict[str, Any]]
    provider: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.0
    max_tokens: Optional[int] = 512
    enable_semantic: bool = False
    semantic_threshold: float = 0.8
    enable_toxicity: bool = False
    toxicity_terms: List[str] = []
    enable_hallucination: bool = False


class ValidationJobResult(BaseModel):
    test_case_id: str
    total_passed: int
    total_failed: int
    duration_ms: float
    provider: str
    model: str
    semantic_failed: int = 0
    toxicity_hits: int = 0
    hallucination_hits: int = 0
