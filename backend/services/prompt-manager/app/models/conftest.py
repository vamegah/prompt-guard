import importlib
import sys
from pathlib import Path

import pytest
from unittest.mock import AsyncMock

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

base = Path(__file__).resolve().parents[2]
base_path = str(base)
if base_path in sys.path:
    sys.path.remove(base_path)
sys.path.insert(0, base_path)

def _endpoint_modules():
    return (
        importlib.import_module("app.models.prompts"),
        importlib.import_module("app.models.schemas"),
        importlib.import_module("app.models.test_suites"),
    )


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """
    Create a FastAPI app instance for testing, including all routers.
    This app is shared across all tests in a session for efficiency.
    """
    prompts, schemas, test_suites = _endpoint_modules()
    test_app = FastAPI(title="Test App")
    test_app.include_router(prompts.router, prefix="/prompts", tags=["Prompts"])
    test_app.include_router(schemas.router, prefix="/schemas", tags=["Schemas"])
    test_app.include_router(
        test_suites.router, prefix="/test-suites", tags=["Test Suites"]
    )
    return test_app


@pytest.fixture
def client(app: FastAPI) -> AsyncClient:
    """
    Fixture to create an httpx.AsyncClient for making requests to the test app.
    """
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def mock_repo_factory(monkeypatch):
    """
    A factory fixture to mock any repository class.
    It replaces the target repository class where it's used (in the endpoint)
    with a mock.
    """

    def _mock_repo(repo_class_path: str, repo_spec):
        mock_repo = AsyncMock(spec=repo_spec)
        module_path, attr_name = repo_class_path.rsplit(".", 1)
        target_module = importlib.import_module(module_path)

        def factory(db_session):
            return mock_repo

        monkeypatch.setattr(target_module, attr_name, factory)
        for mounted_module in _endpoint_modules():
            if hasattr(mounted_module, attr_name):
                monkeypatch.setattr(mounted_module, attr_name, factory)
        return mock_repo

    return _mock_repo
