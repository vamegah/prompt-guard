from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    queue_name: str = "validation_jobs"
    processing_queue_name: str = "validation_jobs_processing"
    dlq_queue_name: str = "validation_jobs_dlq"
    llm_gateway_url: str = "http://llm-gateway:8002/api/v1/generate"
    analytics_url: str = "http://analytics:8003/api/v1/metrics"
    internal_api_key: str | None = None
    audit_url: str | None = None
    audit_api_key: str | None = None
    internal_ca_bundle: str | None = None
    internal_client_cert: str | None = None
    internal_client_key: str | None = None
    max_retries: int = 3
    retry_backoff_base_seconds: float = 1.0
    retry_backoff_max_seconds: float = 30.0
    analytics_timeout_seconds: float = 10.0
    llm_timeout_seconds: float = 60.0

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
