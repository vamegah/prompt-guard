import importlib
import os
import tempfile
import uuid

import httpx
import pytest
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

from app.db.base import Base
from app.db.session import get_db
from app.models import Organization, LLMApiKey


def _load_app():
    import app.core.config as config
    import app.core.oidc as oidc
    import app.core.security as security
    import app.main as main

    importlib.reload(config)
    importlib.reload(oidc)
    importlib.reload(security)
    importlib.reload(main)
    return main.app


async def _setup_sqlite(app, org_id: uuid.UUID, encrypted_value: str):
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
        org = Organization(id=org_id, name="Test Org")
        session.add(org)
        session.add(
            LLMApiKey(
                org_id=org_id,
                provider="openai",
                name="primary",
                encrypted_value=encrypted_value,
            )
        )
        await session.commit()

    return engine, tmp.name


@pytest.mark.asyncio
async def test_internal_api_key_resolve():
    org_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    master_key = Fernet.generate_key().decode("utf-8")
    os.environ["MASTER_KEY"] = master_key
    os.environ["SECRET_BACKEND"] = "fernet"
    os.environ["INTERNAL_API_KEY"] = "internal-key"

    import app.core.secrets as secrets
    import app.core.config as config
    importlib.reload(config)
    importlib.reload(secrets)

    app = _load_app()
    encrypted = secrets.encrypt_value("secret")
    engine, db_path = await _setup_sqlite(app, org_id, encrypted)

    await app.router.startup()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                f"/api/v1/internal/orgs/{org_id}/api-keys/openai",
                headers={"X-Internal-Key": "internal-key"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["value"] == "secret"
    finally:
        await app.router.shutdown()
        await engine.dispose()
        os.unlink(db_path)


@pytest.mark.asyncio
async def test_internal_api_key_requires_header():
    org_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    master_key = Fernet.generate_key().decode("utf-8")
    os.environ["MASTER_KEY"] = master_key
    os.environ["SECRET_BACKEND"] = "fernet"
    os.environ["INTERNAL_API_KEY"] = "internal-key"

    import app.core.secrets as secrets
    import app.core.config as config
    importlib.reload(config)
    importlib.reload(secrets)

    app = _load_app()
    encrypted = secrets.encrypt_value("secret")
    engine, db_path = await _setup_sqlite(app, org_id, encrypted)

    await app.router.startup()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                f"/api/v1/internal/orgs/{org_id}/api-keys/openai"
            )
            assert resp.status_code == 401
    finally:
        await app.router.shutdown()
        await engine.dispose()
        os.unlink(db_path)
