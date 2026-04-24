from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    internal_api_key: str | None = None
    audit_url: str | None = None
    audit_api_key: str | None = None
    internal_ca_bundle: str | None = None
    internal_client_cert: str | None = None
    internal_client_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
