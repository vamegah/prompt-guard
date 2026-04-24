import httpx
import pytest


@pytest.mark.asyncio
async def test_generate_basic(set_env, monkeypatch):
    import os
    import importlib
    import app.core.config as config

    os.environ["BILLING_URL"] = "http://billing.local/usage"
    os.environ["BILLING_API_KEY"] = "billing-key"
    importlib.reload(config)

    from app.main import app

    async def fake_generate(self, prompt: str, **kwargs):
        return "ok"

    from promptguard_shared.llm.openai import OpenAIClient

    monkeypatch.setattr(OpenAIClient, "generate", fake_generate, raising=False)

    called = {}

    async def fake_post(self, url, json=None, headers=None):
        called["url"] = url
        called["json"] = json
        called["headers"] = headers
        class Resp:
            status_code = 200

            def raise_for_status(self):
                return None

        return Resp()

    import httpx as httpx_mod
    monkeypatch.setattr(httpx_mod.AsyncClient, "post", fake_post, raising=False)

    await app.router.startup()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.request(
                "POST",
                "/api/v1/generate",
                json={"provider": "openai", "prompt": "hello", "cache": False},
                headers={"X-Org-Id": "org-1", "X-Internal-Key": "internal-key"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["text"] == "ok"
            assert called["url"] == "http://billing.local/usage"
            assert called["headers"] == {"X-API-Key": "billing-key"}
    finally:
        await app.router.shutdown()


@pytest.mark.asyncio
async def test_generate_fetches_org_key(set_env, monkeypatch):
    import os
    import importlib
    import app.core.config as config

    os.environ.pop("OPENAI_API_KEY", None)
    os.environ["PROMPT_MANAGER_URL"] = "http://prompt-manager.local"
    os.environ["PROMPT_MANAGER_INTERNAL_KEY"] = "internal-key"
    importlib.reload(config)

    from app.main import app

    async def fake_generate(self, prompt: str, **kwargs):
        return "ok"

    from promptguard_shared.llm.openai import OpenAIClient
    monkeypatch.setattr(OpenAIClient, "generate", fake_generate, raising=False)

    class FakeResp:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {"value": "org-key"}

    async def fake_get(self, url, headers=None):
        assert url == "http://prompt-manager.local/api/v1/internal/orgs/org-1/api-keys/openai"
        assert headers == {"X-Internal-Key": "internal-key"}
        return FakeResp()

    import httpx as httpx_mod
    monkeypatch.setattr(httpx_mod.AsyncClient, "get", fake_get, raising=False)

    await app.router.startup()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.request(
                "POST",
                "/api/v1/generate",
                json={"provider": "openai", "prompt": "hello", "cache": False},
                headers={"X-Org-Id": "org-1", "X-Internal-Key": "internal-key"},
            )
            assert resp.status_code == 200
    finally:
        await app.router.shutdown()
