from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Table, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

# Association table for many-to-many between test_suites and prompts/schemas
# (A test suite can have multiple prompts and schemas, but typically one each? We'll keep it flexible.)
test_suite_prompts = Table(
    "test_suite_prompts",
    Base.metadata,
    Column("test_suite_id", UUID(as_uuid=True), ForeignKey("test_suites.id")),
    Column("prompt_id", UUID(as_uuid=True), ForeignKey("prompts.id")),
)

test_suite_schemas = Table(
    "test_suite_schemas",
    Base.metadata,
    Column("test_suite_id", UUID(as_uuid=True), ForeignKey("test_suites.id")),
    Column("schema_id", UUID(as_uuid=True), ForeignKey("schemas.id")),
)


class TestSuite(Base):
    __tablename__ = "test_suites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    # Many-to-many relationships
    prompts = relationship("Prompt", secondary=test_suite_prompts)
    schemas = relationship("Schema", secondary=test_suite_schemas)
    # JSON field for test inputs: list of objects with input_data and optional expected_output
    test_inputs = Column(JSON, nullable=False, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Convenience: we can also store a default prompt_id/schema_id if single
    # But for now we'll use relationships.
    # default_prompt_id = Column(UUID(as_uuid=True), ForeignKey("prompts.id"))
