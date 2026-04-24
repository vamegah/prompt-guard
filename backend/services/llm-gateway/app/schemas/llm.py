from pydantic import BaseModel


class LLMGenerateRequest(BaseModel):
    provider: str
    prompt: str
    model: str | None = None
    temperature: float | None = 0.0
    max_tokens: int | None = 512
    cache: bool = True
    cache_key: str | None = None


class LLMGenerateResponse(BaseModel):
    text: str
    provider: str
    model: str
    cost_cents: float
    latency_ms: float
    cached: bool
