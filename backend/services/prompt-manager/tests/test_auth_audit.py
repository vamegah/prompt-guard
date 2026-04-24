import importlib
import os
import tempfile
import uuid
import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

from app.db.base import Base
from app.models import Organization
from app.db.session import get_db


def _load_app(api_key: str | None):
    if api_key is None:
        os.environ.pop("API_KEY", None)
    else:
        os.environ["API_KEY"] = api_key

    import app.core.config as config
    import app.core.oidc as oidc
    import app.core.security as security
    import app.main as main

    importlib.reload(config)
    importlib.reload(oidc)
    importlib.reload(security)
    importlib.reload(main)
    return main.app


async def _setup_sqlite(app):
    SQLiteTypeCompiler.visit_UUID = lambda self, type_, **kw: "TEXT"
    SQLiteTypeCompiler.visit_JSONB = lambda self, type_, **kw: "JSON"

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmp.close()
    db_url = f"sqlite+aiosqlite:///{tmp.name}"
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _override_db():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _override_db

    async with SessionLocal() as session:
        org = Organization(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            name="Test Org",
        )
        session.add(org)
        await session.commit()

    return engine, tmp.name


@pytest.mark.asyncio
async def test_api_key_required(set_env):
    user_id = "22222222-2222-2222-2222-222222222222"
    org_id = "11111111-1111-1111-1111-111111111111"
    app = _load_app("test-key")
    engine, db_path = await _setup_sqlite(app)
    await app.router.startup()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/prompts",
                headers={"X-User-Id": user_id, "X-Org-Id": org_id},
                follow_redirects=True,
            )
            assert resp.status_code == 401
    finally:
        await app.router.shutdown()
        await engine.dispose()
        os.unlink(db_path)


@pytest.mark.asyncio
async def test_api_key_allows_access(set_env):
    user_id = "22222222-2222-2222-2222-222222222222"
    org_id = "11111111-1111-1111-1111-111111111111"
    app = _load_app("test-key")
    engine, db_path = await _setup_sqlite(app)
    await app.router.startup()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/prompts",
                headers={
                    "X-API-Key": "test-key",
                    "X-User-Id": user_id,
                    "X-Org-Id": org_id,
                    "X-Role": "viewer",
                },
                follow_redirects=True,
            )
            assert resp.status_code == 200
    finally:
        await app.router.shutdown()
        await engine.dispose()
        os.unlink(db_path)


@pytest.mark.asyncio
async def test_audit_log_created(set_env):
    user_id = "22222222-2222-2222-2222-222222222222"
    org_id = "11111111-1111-1111-1111-111111111111"
    app = _load_app("test-key")
    engine, db_path = await _setup_sqlite(app)
    await app.router.startup()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            create_resp = await client.post(
                "/api/v1/prompts",
                headers={
                    "X-API-Key": "test-key",
                    "X-Actor": "tester",
                    "X-User-Id": user_id,
                    "X-Org-Id": org_id,
                    "X-Role": "editor",
                },
                follow_redirects=True,
                json={
                    "name": "Test Prompt",
                    "template": "Hello {{input}}",
                    "description": "test",
                    "version": "1.0.0",
                    "metadata": {},
                },
            )
            assert create_resp.status_code == 201

            logs_resp = await client.get(
                "/api/v1/audit-logs",
                headers={
                    "X-API-Key": "test-key",
                    "X-User-Id": user_id,
                    "X-Org-Id": org_id,
                    "X-Role": "admin",
                },
                follow_redirects=True,
            )
            assert logs_resp.status_code == 200
            logs = logs_resp.json()
            assert any(
                log["action"] == "create" and log["resource"] == "prompt"
                for log in logs
            )
    finally:
        await app.router.shutdown()
        await engine.dispose()
        os.unlink(db_path)
