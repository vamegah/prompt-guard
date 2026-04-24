from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

from cryptography.fernet import Fernet
import httpx

from app.core.config import settings


class SecretsError(RuntimeError):
    pass


class SecretProvider:
    name: str = "base"
    supports_rewrap: bool = False
    supports_rotate: bool = False

    def encrypt(self, value: str) -> str:
        raise NotImplementedError

    def decrypt(self, value: str) -> str:
        raise NotImplementedError

    def rewrap(self, value: str) -> str:
        raise NotImplementedError

    def rotate_key(self) -> None:
        raise NotImplementedError


@dataclass
class FernetProvider(SecretProvider):
    name: str = "fernet"

    def _get_fernet(self) -> Fernet:
        if not settings.MASTER_KEY:
            raise SecretsError("MASTER_KEY is not configured")
        return Fernet(settings.MASTER_KEY)

    def encrypt(self, value: str) -> str:
        return self._get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, value: str) -> str:
        return self._get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")


@dataclass
class VaultTransitProvider(SecretProvider):
    name: str = "vault"
    supports_rewrap: bool = True
    supports_rotate: bool = True

    def _base_url(self) -> str:
        if not settings.VAULT_ADDR:
            raise SecretsError("VAULT_ADDR is not configured")
        if not settings.VAULT_TRANSIT_KEY:
            raise SecretsError("VAULT_TRANSIT_KEY is not configured")
        mount = settings.VAULT_TRANSIT_MOUNT or "transit"
        return f"{settings.VAULT_ADDR.rstrip('/')}/v1/{mount}"

    def _headers(self) -> dict[str, str]:
        if not settings.VAULT_TOKEN:
            raise SecretsError("VAULT_TOKEN is not configured")
        headers = {"X-Vault-Token": settings.VAULT_TOKEN}
        if settings.VAULT_NAMESPACE:
            headers["X-Vault-Namespace"] = settings.VAULT_NAMESPACE
        return headers

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url()}/{path}"
        resp = httpx.post(url, headers=self._headers(), json=payload, timeout=10)
        if resp.status_code >= 400:
            raise SecretsError(f"Vault error {resp.status_code}: {resp.text}")
        data = resp.json()
        if "data" not in data:
            raise SecretsError("Vault response missing data")
        return data["data"]

    def encrypt(self, value: str) -> str:
        plaintext = base64.b64encode(value.encode("utf-8")).decode("utf-8")
        data = self._post(f"encrypt/{settings.VAULT_TRANSIT_KEY}", {"plaintext": plaintext})
        return data["ciphertext"]

    def decrypt(self, value: str) -> str:
        data = self._post(f"decrypt/{settings.VAULT_TRANSIT_KEY}", {"ciphertext": value})
        plaintext = data.get("plaintext")
        if not plaintext:
            raise SecretsError("Vault decrypt response missing plaintext")
        return base64.b64decode(plaintext.encode("utf-8")).decode("utf-8")

    def rewrap(self, value: str) -> str:
        data = self._post(f"rewrap/{settings.VAULT_TRANSIT_KEY}", {"ciphertext": value})
        return data["ciphertext"]

    def rotate_key(self) -> None:
        self._post(f"keys/{settings.VAULT_TRANSIT_KEY}/rotate", {})


@dataclass
class AwsKmsProvider(SecretProvider):
    name: str = "aws_kms"
    supports_rewrap: bool = True

    def _client(self):
        try:
            import boto3
        except Exception as exc:  # pragma: no cover - optional dependency
            raise SecretsError("boto3 is required for aws_kms backend") from exc
        if not settings.AWS_REGION:
            raise SecretsError("AWS_REGION is not configured")
        return boto3.client("kms", region_name=settings.AWS_REGION)

    def _key_id(self) -> str:
        if not settings.AWS_KMS_KEY_ID:
            raise SecretsError("AWS_KMS_KEY_ID is not configured")
        return settings.AWS_KMS_KEY_ID

    def _context(self) -> dict[str, str] | None:
        context = settings.AWS_KMS_ENCRYPTION_CONTEXT
        if not context:
            return None
        return {str(k): str(v) for k, v in context.items()}

    def encrypt(self, value: str) -> str:
        client = self._client()
        params = {"KeyId": self._key_id(), "Plaintext": value.encode("utf-8")}
        context = self._context()
        if context:
            params["EncryptionContext"] = context
        resp = client.encrypt(**params)
        return base64.b64encode(resp["CiphertextBlob"]).decode("utf-8")

    def decrypt(self, value: str) -> str:
        client = self._client()
        params = {"CiphertextBlob": base64.b64decode(value.encode("utf-8"))}
        context = self._context()
        if context:
            params["EncryptionContext"] = context
        resp = client.decrypt(**params)
        return resp["Plaintext"].decode("utf-8")

    def rewrap(self, value: str) -> str:
        client = self._client()
        params = {
            "CiphertextBlob": base64.b64decode(value.encode("utf-8")),
            "DestinationKeyId": self._key_id(),
        }
        context = self._context()
        if context:
            params["DestinationEncryptionContext"] = context
        resp = client.re_encrypt(**params)
        return base64.b64encode(resp["CiphertextBlob"]).decode("utf-8")


_provider: SecretProvider | None = None


def get_provider() -> SecretProvider:
    global _provider
    if _provider:
        return _provider
    backend = (settings.SECRET_BACKEND or "fernet").lower()
    if backend == "vault":
        _provider = VaultTransitProvider()
    elif backend in {"aws_kms", "kms"}:
        _provider = AwsKmsProvider()
    elif backend in {"fernet", "local"}:
        _provider = FernetProvider()
    else:
        raise SecretsError(f"Unsupported SECRET_BACKEND: {backend}")
    return _provider


def encrypt_value(value: str) -> str:
    return get_provider().encrypt(value)


def decrypt_value(value: str) -> str:
    return get_provider().decrypt(value)


def rewrap_value(value: str) -> str:
    provider = get_provider()
    if not provider.supports_rewrap:
        raise SecretsError(f"Secret backend {provider.name} does not support rewrap")
    return provider.rewrap(value)


def rotate_backend_key() -> None:
    provider = get_provider()
    if not provider.supports_rotate:
        raise SecretsError(f"Secret backend {provider.name} does not support key rotation")
    provider.rotate_key()
