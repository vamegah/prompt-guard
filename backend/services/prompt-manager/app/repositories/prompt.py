from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Prompt
from app.repositories.base import BaseRepository


class PromptRepository(BaseRepository[Prompt]):
    """
    Repository for Prompt model, extending generic CRUD operations.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Prompt, db_session)
