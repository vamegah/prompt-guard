from pydantic import BaseModel


class ValidationMetric(BaseModel):
    test_case_id: str
    total_passed: int
    total_failed: int
    duration_ms: float
    provider: str
    model: str
    semantic_failed: int = 0
    toxicity_hits: int = 0
    hallucination_hits: int = 0
