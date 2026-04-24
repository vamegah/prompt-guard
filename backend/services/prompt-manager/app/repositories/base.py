from typing import Generic, TypeVar, Type, List, Optional, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

# Define a type variable for the SQLAlchemy model
ModelType = TypeVar("ModelType", bound=declarative_base())


class BaseRepository(Generic[ModelType]):
    """
    A generic repository class for common CRUD operations on a SQLAlchemy model.
    """

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def create(self, obj_in: Union[Dict[str, Any], BaseModel]) -> ModelType:
        """
        Creates a new record in the database.
        :param obj_in: A dictionary or Pydantic model of attributes for the new object.
        :return: The created model instance.
        """
        if isinstance(obj_in, BaseModel):
            obj_in_data = obj_in.model_dump()
        else:
            obj_in_data = obj_in
        db_obj = self.model(**obj_in_data)
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def get(self, id: UUID) -> Optional[ModelType]:
        """
        Retrieves a single record by its ID.
        :param id: The UUID of the record to retrieve.
        :return: The model instance if found, otherwise None.
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Retrieves multiple records.
        :param skip: The number of records to skip.
        :param limit: The maximum number of records to return.
        :return: A list of model instances.
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, db_obj: ModelType, obj_in: Union[Dict[str, Any], BaseModel]
    ) -> ModelType:
        """
        Updates an existing record.
        :param db_obj: The existing model instance to update.
        :param obj_in: A dictionary or Pydantic model of attributes to update.
        :return: The updated model instance.
        """
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelType) -> None:
        """
        Deletes a record from the database.
        :param db_obj: The model instance to delete.
        """
        await self.db_session.delete(db_obj)
        await self.db_session.commit()
