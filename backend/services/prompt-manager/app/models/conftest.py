import pytest
from unittest.mock import AsyncMock

from fastapi import FastAPI
from httpx import AsyncClient

# The context shows endpoint files in the 'models' directory, which is unusual.
# We'll follow that structure for imports. If you move them to `app/api/endpoints`,
# you would update these imports accordingly.
from app.models import prompts, schemas, test_suites


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """
    Create a FastAPI app instance for testing, including all routers.
    This app is shared across all tests in a session for efficiency.
    """
    test_app = FastAPI(title="Test App")
    test_app.include_router(prompts.router, prefix="/prompts", tags=["Prompts"])
    test_app.include_router(schemas.router, prefix="/schemas", tags=["Schemas"])
    test_app.include_router(
        test_suites.router, prefix="/test-suites", tags=["Test Suites"]
    )
    return test_app


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    """
    Fixture to create an httpx.AsyncClient for making requests to the test app.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_repo_factory(monkeypatch):
    """
    A factory fixture to mock any repository class.
    It replaces the target repository class where it's used (in the endpoint)
    with a mock.
    """

    def _mock_repo(repo_class_path: str, repo_spec):
        mock_repo = AsyncMock(spec=repo_spec)
        # The lambda ensures that when the endpoint code calls `Repository(db)`,
        # it gets our mock instance instead of creating a new real one.
        monkeypatch.setattr(repo_class_path, lambda db_session: mock_repo)
        return mock_repo

    return _mock_repo
