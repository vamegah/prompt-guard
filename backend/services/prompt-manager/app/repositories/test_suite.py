from sqlalchemy.ext.asyncio import AsyncSession
from app.models.test_suite import TestSuite
from app.repositories.base import BaseRepository


class TestSuiteRepository(BaseRepository[TestSuite]):
    """
    Repository for TestSuite model, extending generic CRUD operations.
    Specific TestSuite-related queries can be added here.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(TestSuite, db_session)
