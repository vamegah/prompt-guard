import importlib
import os

import pytest


def _reload_settings():
    import app.core.config as config
    import app.core.oidc as oidc

    importlib.reload(config)
    importlib.reload(oidc)
    return config.settings


def _enable_oidc():
    os.environ["OIDC_ENABLED"] = "true"
    os.environ["OIDC_ISSUER"] = "https://issuer.example"
    os.environ["OIDC_AUDIENCE"] = "promptguard"
    os.environ["OIDC_JWKS_URL"] = "https://issuer.example/.well-known/jwks.json"


def _disable_oidc():
    os.environ["OIDC_ENABLED"] = "false"


def test_oidc_requires_bearer():
    _enable_oidc()
    _reload_settings()

    import app.core.oidc as oidc

    with pytest.raises(Exception) as exc:
        oidc.get_current_principal(authorization=None)
    assert getattr(exc.value, "detail", None) == "Missing bearer token"


def test_oidc_accepts_valid_token(monkeypatch):
    _enable_oidc()
    _reload_settings()

    class FakeSigningKey:
        def __init__(self):
            self.key = "fake"

    class FakeJWKClient:
        def __init__(self, url: str):
            self.url = url

        def get_signing_key_from_jwt(self, token: str):
            return FakeSigningKey()

    def fake_decode(token, key, algorithms, audience, issuer):
        return {"sub": "user-1", "org_id": "org-1"}

    import app.core.oidc as oidc
    import jwt as pyjwt

    monkeypatch.setattr(oidc, "PyJWKClient", FakeJWKClient)
    monkeypatch.setattr(pyjwt, "decode", fake_decode)

    principal = oidc.get_current_principal(authorization="Bearer faketoken")
    assert principal.user_id == "user-1"
    assert principal.org_id == "org-1"


def test_oidc_disabled_accepts_headers():
    _disable_oidc()
    _reload_settings()

    import app.core.oidc as oidc

    principal = oidc.get_current_principal(
        authorization=None, x_user_id="user-1", x_org_id="org-1"
    )
    assert principal.user_id == "user-1"
    assert principal.org_id == "org-1"
