from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict


class Settings(BaseSettings):
    environment: str = "development"
    require_org_scoped_keys: bool = False
    redis_url: str = "redis://localhost:6379/1"
    cache_ttl_seconds: int = 3600
    cache_namespace: str = "llm_gateway"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    default_models: Dict[str, str] = {"openai": "gpt-4", "anthropic": "claude-3-opus-20240229"}
    billing_url: str | None = None
    billing_api_key: str | None = None
    internal_api_key: str | None = None
    audit_url: str | None = None
    audit_api_key: str | None = None
    prompt_manager_url: str | None = None
    prompt_manager_internal_key: str | None = None
    internal_ca_bundle: str | None = None
    internal_client_cert: str | None = None
    internal_client_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
