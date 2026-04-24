from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "Prompt Manager"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = (
        "postgresql+asyncpg://promptguard:promptguard@localhost:5432/promptguard"
    )
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    API_KEY: str | None = None
    MASTER_KEY: str | None = None
    INTERNAL_API_KEY: str | None = None
    SIEM_WEBHOOK_URL: str | None = None
    SIEM_API_KEY: str | None = None
    AUDIT_RETENTION_DAYS: int = 90
    AUDIT_RETENTION_ENABLED: bool = False
    AUDIT_RETENTION_INTERVAL_HOURS: int = 24
    SECRET_ROTATION_ENABLED: bool = False
    SECRET_ROTATION_INTERVAL_HOURS: int = 24
    SECRET_BACKEND: str = "fernet"
    VAULT_ADDR: str | None = None
    VAULT_TOKEN: str | None = None
    VAULT_NAMESPACE: str | None = None
    VAULT_TRANSIT_MOUNT: str = "transit"
    VAULT_TRANSIT_KEY: str | None = None
    AWS_REGION: str | None = None
    AWS_KMS_KEY_ID: str | None = None
    AWS_KMS_ENCRYPTION_CONTEXT: dict | None = None
    OIDC_ENABLED: bool = False
    OIDC_ISSUER: str | None = None
    OIDC_AUDIENCE: str | None = None
    OIDC_JWKS_URL: str | None = None
    OIDC_ALLOWED_ALGS: List[str] = ["RS256"]
    AUTO_CREATE_TABLES: bool = False
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_STORAGE_URL: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

    @field_validator("AWS_KMS_ENCRYPTION_CONTEXT", mode="before")
    @classmethod
    def _parse_kms_context(cls, value):
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            if value.strip() == "":
                return None
            return json.loads(value)
        return value


settings = Settings()
