import httpx
import pytest

from app.main import app


@pytest.mark.asyncio
async def test_adversarial_generation(set_env):
    await app.router.startup()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/adversarial",
                json={"base_inputs": [{"input": "hello"}], "count_per_input": 2},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "generated" in data
            assert len(data["generated"]) == 2
    finally:
        await app.router.shutdown()
