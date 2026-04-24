from pydantic import BaseModel
from typing import Any, Dict, List


class AdversarialRequest(BaseModel):
    base_inputs: List[Dict[str, Any]]
    count_per_input: int = 6


class AdversarialResponse(BaseModel):
    generated: List[Dict[str, Any]]


class AdversarialValidationRequest(BaseModel):
    test_case_id: str
    prompt_template: str
    json_schema: Dict[str, Any]
    base_inputs: List[Dict[str, Any]]
    provider: str
    model: str | None = None
    temperature: float | None = 0.0
    max_tokens: int | None = 512
    count_per_input: int = 6
    enable_semantic: bool = False
    semantic_threshold: float = 0.8
    enable_toxicity: bool = False
    toxicity_terms: List[str] = []
    enable_hallucination: bool = False


class AdversarialValidationResponse(BaseModel):
    status: str
    test_case_id: str
    generated_count: int
