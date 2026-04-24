import httpx

from app.core.config import settings


def build_http_client(timeout_seconds: float) -> httpx.AsyncClient:
    verify: bool | str = True
    if settings.internal_ca_bundle:
        verify = settings.internal_ca_bundle

    cert = None
    if settings.internal_client_cert and settings.internal_client_key:
        cert = (settings.internal_client_cert, settings.internal_client_key)
    elif settings.internal_client_cert:
        cert = settings.internal_client_cert

    return httpx.AsyncClient(timeout=timeout_seconds, verify=verify, cert=cert)
