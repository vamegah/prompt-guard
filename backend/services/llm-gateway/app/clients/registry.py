from enum import Enum
from typing import Callable

from promptguard_shared.llm.anthropic import AnthropicClient
from promptguard_shared.llm.openai import OpenAIClient


class Provider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"


ClientFactory = Callable[[str, str], object]


def get_client_factory(provider: Provider) -> ClientFactory:
    if provider == Provider.openai:
        return lambda api_key, model: OpenAIClient(api_key=api_key, model=model)
    if provider == Provider.anthropic:
        return lambda api_key, model: AnthropicClient(api_key=api_key, model=model)
    raise ValueError(f"Unsupported provider: {provider}")
