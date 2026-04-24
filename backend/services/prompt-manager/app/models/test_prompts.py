import pytest
from uuid import uuid4, UUID
from datetime import datetime
from unittest.mock import AsyncMock

from httpx import AsyncClient
from fastapi import status


# --- Test Setup ---


@pytest.fixture
def mock_prompt_repo(mock_repo_factory):
    """
    Mocks the PromptRepository for prompt-related tests by using the
    generic factory from conftest.py.
    """
    return mock_repo_factory(
        # Path to the Repository class inside the endpoint module we are testing
        "app.models.prompts.PromptRepository",
        PromptRepository,
    )


# --- Test Cases ---


@pytest.mark.asyncio
class TestCreatePrompt:
    async def test_create_prompt_success(
        self, client: AsyncClient, mock_prompt_repo: AsyncMock
    ):
        """Tests successful creation of a new prompt."""
        create_data = {
            "name": "New Test Prompt",
            "template": "Hello, {{name}}!",
            "description": "A prompt for testing purposes",
            "version": "1.0.0",
            "metadata": {"author": "Test User"},
        }

        # Define what the mocked repository should return
        mock_created_prompt = {
            "id": uuid4(),
            "created_at": datetime.utcnow(),
            "updated_at": None,
            **create_data,
        }
        mock_prompt_repo.create.return_value = mock_created_prompt

        response = await client.post("/prompts/", json=create_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == create_data["name"]
        assert "id" in response_data
        assert "created_at" in response_data

        mock_prompt_repo.create.assert_awaited_once()

    async def test_create_prompt_invalid_payload(self, client: AsyncClient):
        """Tests that creating a prompt with an invalid payload returns a 422 error."""
        # Missing 'name' and 'template' which are required
        invalid_data = {"description": "This payload is invalid"}

        response = await client.post("/prompts/", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
class TestGetPrompt:
    async def test_get_prompt_success(
        self, client: AsyncClient, mock_prompt_repo: AsyncMock
    ):
        """Tests successful retrieval of an existing prompt."""
        test_id = uuid4()
        mock_existing_prompt = {
            "id": test_id,
            "name": "Existing Prompt",
            "template": "Test template",
            "created_at": datetime.utcnow(),
            "updated_at": None,
        }
        mock_prompt_repo.get.return_value = mock_existing_prompt

        response = await client.get(f"/prompts/{test_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(test_id)
        assert response.json()["name"] == "Existing Prompt"
        mock_prompt_repo.get.assert_awaited_once_with(test_id)

    async def test_get_prompt_not_found(
        self, client: AsyncClient, mock_prompt_repo: AsyncMock
    ):
        """Tests that retrieving a non-existent prompt returns a 404 error."""
        test_id = uuid4()
        mock_prompt_repo.get.return_value = None  # Simulate not finding the prompt

        response = await client.get(f"/prompts/{test_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Prompt not found"
        mock_prompt_repo.get.assert_awaited_once_with(test_id)


@pytest.mark.asyncio
class TestUpdatePrompt:
    async def test_update_prompt_success(
        self, client: AsyncClient, mock_prompt_repo: AsyncMock
    ):
        """Tests successful update of an existing prompt."""
        test_id = uuid4()
        update_data = {"name": "Updated Prompt Name", "description": "New description"}

        mock_existing_prompt = {
            "id": test_id,
            "name": "Old Name",
            "template": "Old template",
            "created_at": datetime.utcnow(),
            "updated_at": None,
        }
        mock_updated_prompt = {
            **mock_existing_prompt,
            **update_data,
            "updated_at": datetime.utcnow(),
        }
        mock_prompt_repo.get.return_value = mock_existing_prompt
        mock_prompt_repo.update.return_value = mock_updated_prompt

        response = await client.put(f"/prompts/{test_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Updated Prompt Name"
        mock_prompt_repo.get.assert_awaited_once_with(test_id)
        mock_prompt_repo.update.assert_awaited_once()

    async def test_update_prompt_not_found(
        self, client: AsyncClient, mock_prompt_repo: AsyncMock
    ):
        """Tests that updating a non-existent prompt returns a 404 error."""
        test_id = uuid4()
        mock_prompt_repo.get.return_value = None  # Simulate not finding the prompt

        response = await client.put(
            f"/prompts/{test_id}", json={"name": "Doesn't matter"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Prompt not found"
        mock_prompt_repo.update.assert_not_awaited()


@pytest.mark.asyncio
class TestDeletePrompt:
    async def test_delete_prompt_success(
        self, client: AsyncClient, mock_prompt_repo: AsyncMock
    ):
        """Tests successful deletion of an existing prompt."""
        test_id = uuid4()
        mock_existing_prompt = {"id": test_id, "name": "Prompt to delete"}
        mock_prompt_repo.get.return_value = mock_existing_prompt

        response = await client.delete(f"/prompts/{test_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_prompt_repo.get.assert_awaited_once_with(test_id)
        mock_prompt_repo.delete.assert_awaited_once_with(mock_existing_prompt)

    async def test_delete_prompt_not_found(
        self, client: AsyncClient, mock_prompt_repo: AsyncMock
    ):
        """Tests that deleting a non-existent prompt returns a 404 error."""
        test_id = uuid4()
        mock_prompt_repo.get.return_value = None  # Simulate not finding the prompt

        response = await client.delete(f"/prompts/{test_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Prompt not found"
        mock_prompt_repo.delete.assert_not_awaited()
