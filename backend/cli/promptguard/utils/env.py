import os
from typing import Optional


def get_api_key(provider: str) -> Optional[str]:
    """Get API key for the given provider from environment variables."""
    env_var = f"{provider.upper()}_API_KEY"
    return os.getenv(env_var)
