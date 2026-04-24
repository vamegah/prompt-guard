from sqlalchemy import Column, String, Integer
from app.db.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    monthly_price_cents = Column(Integer, nullable=False, default=0)
    included_validation_runs = Column(Integer, nullable=False, default=0)
    included_llm_calls = Column(Integer, nullable=False, default=0)
