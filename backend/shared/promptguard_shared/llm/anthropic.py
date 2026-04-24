import anthropic
from typing import Any
from .base import LLMClient, LLMResponse


class AnthropicClient(LLMClient):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        content = response.content[0].text
        usage = getattr(response, "usage", None)
        if usage is None and isinstance(response, dict):
            usage = response.get("usage")
        return LLMResponse(text=content, raw=response, usage=usage, model=self.model)

    def get_cost(self, response: Any) -> float:
        if hasattr(response, "usage"):
            usage = response.usage
        elif hasattr(response, "raw") and hasattr(response.raw, "usage"):
            usage = response.raw.usage
        elif isinstance(response, dict):
            usage = response.get("usage")
        elif hasattr(response, "raw") and isinstance(response.raw, dict):
            usage = response.raw.get("usage")
        else:
            usage = None

        if usage:
            prompt_tokens = getattr(usage, "prompt_tokens", None) or usage.get("prompt_tokens", 0)
            completion_tokens = getattr(usage, "completion_tokens", None) or usage.get("completion_tokens", 0)
            # Use a conservative estimate for Claude-like pricing
            rate_per_1k = 0.003
            return float(((prompt_tokens + completion_tokens) / 1000) * rate_per_1k)

        total_tokens = getattr(usage, "total_tokens", None) or usage.get("total_tokens", None) if usage else None
        if total_tokens is not None:
            return float((total_tokens / 1000) * 0.003)

        return 0.0
