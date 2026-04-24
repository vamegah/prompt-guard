import importlib
import os
import base64
import sys

import pytest


def _reload_modules():
    import app.core.config as config
    import app.core.secrets as secrets

    importlib.reload(config)
    importlib.reload(secrets)
    return config.settings, secrets


def test_vault_transit_encrypt_decrypt_rewrap(monkeypatch):
    monkeypatch.setenv("SECRET_BACKEND", "vault")
    monkeypatch.setenv("VAULT_ADDR", "http://vault")
    monkeypatch.setenv("VAULT_TOKEN", "token")
    monkeypatch.setenv("VAULT_TRANSIT_KEY", "promptguard")

    settings, secrets = _reload_modules()
    secrets._provider = None

    class _Resp:
        status_code = 200

        def __init__(self, data):
            self._data = data

        def json(self):
            return {"data": self._data}

        @property
        def text(self):
            return "ok"

    def fake_post(url, headers=None, json=None, timeout=None):
        if url.endswith("/encrypt/promptguard"):
            plaintext = json["plaintext"]
            return _Resp({"ciphertext": f"vault:v1:{plaintext}"})
        if url.endswith("/decrypt/promptguard"):
            ciphertext = json["ciphertext"]
            plaintext = ciphertext.split("vault:v1:")[1]
            return _Resp({"plaintext": plaintext})
        if url.endswith("/rewrap/promptguard"):
            ciphertext = json["ciphertext"]
            return _Resp({"ciphertext": ciphertext.replace("v1", "v2")})
        if url.endswith("/keys/promptguard/rotate"):
            return _Resp({})
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(secrets.httpx, "post", fake_post)

    encrypted = secrets.encrypt_value("hello")
    assert encrypted.startswith("vault:v1:")
    decrypted = secrets.decrypt_value(encrypted)
    assert decrypted == "hello"
    rewrapped = secrets.rewrap_value(encrypted)
    assert "v2" in rewrapped
    secrets.rotate_backend_key()


def test_kms_encrypt_decrypt_rewrap(monkeypatch):
    monkeypatch.setenv("SECRET_BACKEND", "aws_kms")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_KMS_KEY_ID", "key-123")

    settings, secrets = _reload_modules()
    secrets._provider = None
    settings.AWS_KMS_ENCRYPTION_CONTEXT = {"org": "1"}

    class FakeKms:
        def encrypt(self, **kwargs):
            assert kwargs["KeyId"] == "key-123"
            assert kwargs["EncryptionContext"] == {"org": "1"}
            return {"CiphertextBlob": b"ciphertext"}

        def decrypt(self, **kwargs):
            assert kwargs["CiphertextBlob"] == b"ciphertext"
            assert kwargs["EncryptionContext"] == {"org": "1"}
            return {"Plaintext": b"secret"}

        def re_encrypt(self, **kwargs):
            assert kwargs["DestinationKeyId"] == "key-123"
            assert kwargs["DestinationEncryptionContext"] == {"org": "1"}
            return {"CiphertextBlob": b"ciphertext-v2"}

    class FakeBotoModule:
        def client(self, name, region_name=None):
            assert name == "kms"
            assert region_name == "us-east-1"
            return FakeKms()

    monkeypatch.setitem(sys.modules, "boto3", FakeBotoModule())

    encrypted = secrets.encrypt_value("secret")
    assert base64.b64decode(encrypted.encode("utf-8")) == b"ciphertext"
    decrypted = secrets.decrypt_value(encrypted)
    assert decrypted == "secret"
    rewrapped = secrets.rewrap_value(encrypted)
    assert base64.b64decode(rewrapped.encode("utf-8")) == b"ciphertext-v2"


def test_unsupported_backend(monkeypatch):
    monkeypatch.setenv("SECRET_BACKEND", "nope")
    settings, secrets = _reload_modules()
    secrets._provider = None
    with pytest.raises(Exception):
        secrets.encrypt_value("hello")
