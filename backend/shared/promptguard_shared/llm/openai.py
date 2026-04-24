import openai
from typing import Optional, Any
from .base import LLMClient, LLMResponse


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        openai.api_key = api_key
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=api_key)  # assuming v1.0+

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}], **kwargs
        )
        content = response.choices[0].message.content
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

        prompt_rate = 0.03 if "gpt-4" in self.model else 0.0015
        completion_rate = 0.06 if "gpt-4" in self.model else 0.002

        if usage:
            prompt_tokens = getattr(usage, "prompt_tokens", None) or usage.get("prompt_tokens", 0)
            completion_tokens = getattr(usage, "completion_tokens", None) or usage.get("completion_tokens", 0)
            total_cost = (prompt_tokens / 1000) * prompt_rate + (completion_tokens / 1000) * completion_rate
            return float(total_cost)

        # Fallback: estimate cost using the full token count if available
        total_tokens = getattr(usage, "total_tokens", None) or usage.get("total_tokens", None) if usage else None
        if total_tokens is not None:
            average_rate = (prompt_rate + completion_rate) / 2
            return float((total_tokens / 1000) * average_rate)

        return 0.0
