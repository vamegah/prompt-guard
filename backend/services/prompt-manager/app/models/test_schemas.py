import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock

from httpx import AsyncClient
from fastapi import status

from app.repositories import SchemaRepository

# --- Test Setup ---


@pytest.fixture
def mock_schema_repo(mock_repo_factory):
    """
    Mocks the SchemaRepository for schema-related tests by using the
    generic factory from conftest.py.
    """
    return mock_repo_factory(
        # Path to the Repository class inside the endpoint module we are testing
        "app.models.schemas.SchemaRepository",
        SchemaRepository,
    )


# --- Test Cases ---


@pytest.mark.asyncio
class TestCreateSchema:
    async def test_create_schema_success(
        self, client: AsyncClient, mock_schema_repo: AsyncMock
    ):
        """Tests successful creation of a new schema."""
        create_data = {
            "name": "New Test Schema",
            "description": "A schema for testing",
            "json_schema": {"type": "object"},
        }

        # Define what the mocked repository should return
        mock_created_schema = {
            "id": uuid4(),
            "name": create_data["name"],
            "description": create_data["description"],
            "json_schema": create_data["json_schema"],
            "created_at": datetime.utcnow(),
            "updated_at": None,
        }
        mock_schema_repo.create.return_value = mock_created_schema

        response = await client.post("/schemas/", json=create_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == create_data["name"]
        assert "id" in response_data

        # Assert that the mock's create method was called once.
        # The argument will be the Pydantic model from the request body.
        mock_schema_repo.create.assert_awaited_once()

    async def test_create_schema_invalid_payload(self, client: AsyncClient):
        """Tests that creating a schema with an invalid payload returns a 422 error."""
        # The 'name' and 'json_schema' fields are missing
        invalid_data = {"description": "This payload is invalid"}

        response = await client.post("/schemas/", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
class TestUpdateSchema:
    async def test_update_schema_success(
        self, client: AsyncClient, mock_schema_repo: AsyncMock
    ):
        """Tests successful update of an existing schema."""
        test_id = uuid4()
        update_data = {"name": "Updated Schema", "description": "New description"}

        # Define what the mocked repository should return
        mock_existing_schema = {"id": test_id, "name": "Old Name"}
        mock_updated_schema = {
            "id": test_id,
            "name": "Updated Schema",
            "description": "New description",
            "json_schema": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        mock_schema_repo.get.return_value = mock_existing_schema
        mock_schema_repo.update.return_value = mock_updated_schema

        response = await client.put(f"/schemas/{test_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Updated Schema"
        mock_schema_repo.get.assert_awaited_once_with(test_id)
        mock_schema_repo.update.assert_awaited_once()

    async def test_update_schema_not_found(
        self, client: AsyncClient, mock_schema_repo: AsyncMock
    ):
        """Tests that updating a non-existent schema returns a 404 error."""
        test_id = uuid4()
        mock_schema_repo.get.return_value = None  # Simulate not finding the schema

        response = await client.put(
            f"/schemas/{test_id}", json={"name": "Doesn't matter"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Schema not found"
        mock_schema_repo.update.assert_not_awaited()


@pytest.mark.asyncio
class TestDeleteSchema:
    async def test_delete_schema_success(
        self, client: AsyncClient, mock_schema_repo: AsyncMock
    ):
        """Tests successful deletion of an existing schema."""
        test_id = uuid4()
        mock_existing_schema = {"id": test_id, "name": "Schema to delete"}
        mock_schema_repo.get.return_value = mock_existing_schema

        response = await client.delete(f"/schemas/{test_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_schema_repo.get.assert_awaited_once_with(test_id)
        mock_schema_repo.delete.assert_awaited_once_with(mock_existing_schema)

    async def test_delete_schema_not_found(
        self, client: AsyncClient, mock_schema_repo: AsyncMock
    ):
        """Tests that deleting a non-existent schema returns a 404 error."""
        test_id = uuid4()
        mock_schema_repo.get.return_value = None  # Simulate not finding the schema

        response = await client.delete(f"/schemas/{test_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Schema not found"
        mock_schema_repo.delete.assert_not_awaited()
