from sqlalchemy import Column, String, Table, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

prompt_tags_association = Table(
    "prompt_tags",
    Base.metadata,
    Column("prompt_id", UUID(as_uuid=True), ForeignKey("prompts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

schema_tags_association = Table(
    "schema_tags",
    Base.metadata,
    Column("schema_id", UUID(as_uuid=True), ForeignKey("schemas.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    prompts = relationship("Prompt", secondary=prompt_tags_association, back_populates="tags")
    schemas = relationship("Schema", secondary=schema_tags_association, back_populates="tags")
