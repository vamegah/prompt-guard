from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Schema
from app.repositories.base import BaseRepository


class SchemaRepository(BaseRepository[Schema]):
    """
    Repository for Schema model, extending generic CRUD operations.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Schema, db_session)
