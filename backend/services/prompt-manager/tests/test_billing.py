from datetime import datetime, timezone
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.jobs.invoice_rollup import create_invoice_rollups, month_bounds
from app.models import UsageEvent, Invoice
from app.api import billing


from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, Column, String
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

TestBase = declarative_base()
TestBase.__test__ = False
Table(
    "organizations",
    TestBase.metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
)
UsageEvent.__table__.to_metadata(TestBase.metadata)
Invoice.__table__.to_metadata(TestBase.metadata)


def _prepare_sqlite(conn):
    SQLiteTypeCompiler.visit_UUID = lambda self, type_, **kw: "BLOB"


@pytest.mark.asyncio
async def test_invoice_rollup_creates_invoices():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(_prepare_sqlite)
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)

    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as db:
        org_a = UUID("11111111-1111-1111-1111-111111111111")
        org_b = UUID("22222222-2222-2222-2222-222222222222")
        occurred_at = datetime(2026, 3, 15, tzinfo=timezone.utc)
        db.add_all(
            [
                UsageEvent(
                    org_id=org_a,
                    event_type="llm_call",
                    units=3,
                    cost_cents=15,
                    created_at=occurred_at,
                ),
                UsageEvent(
                    org_id=org_a,
                    event_type="llm_call",
                    units=2,
                    cost_cents=10,
                    created_at=occurred_at,
                ),
                UsageEvent(
                    org_id=org_b,
                    event_type="llm_call",
                    units=1,
                    cost_cents=5,
                    created_at=occurred_at,
                ),
            ]
        )
        await db.commit()

        start, end = month_bounds(datetime(2026, 3, 1, tzinfo=timezone.utc))
        created = await create_invoice_rollups(db, start, end)
        assert created == 2

        result = await db.execute(select(Invoice))
        invoices = result.scalars().all()
        assert len(invoices) == 2

    await engine.dispose()


@pytest.mark.asyncio
async def test_usage_summary():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(_prepare_sqlite)
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)

    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as db:
        org_id = UUID("33333333-3333-3333-3333-333333333333")
        db.add_all(
            [
                UsageEvent(org_id=org_id, event_type="llm_call", units=2, cost_cents=20),
                UsageEvent(org_id=org_id, event_type="validation", units=1, cost_cents=5),
            ]
        )
        await db.commit()

        summary = await billing.usage_summary(org_id=org_id, db=db)
        assert summary["total_units"] == 3
        assert summary["total_cost_cents"] == 25

    await engine.dispose()
