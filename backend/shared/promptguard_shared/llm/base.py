from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class LLMResponse:
    text: str
    raw: Any
    usage: Optional[Dict[str, Any]] = None
    model: Optional[str] = None


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text from the LLM."""
        pass

    @abstractmethod
    def get_cost(self, response: Any) -> float:
        """Calculate cost of the request."""
        pass
