from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UsageEvent, Invoice


async def create_invoice_rollups(
    db: AsyncSession, period_start: datetime, period_end: datetime
) -> int:
    result = await db.execute(
        select(
            UsageEvent.org_id,
            func.coalesce(func.sum(UsageEvent.units), 0),
            func.coalesce(func.sum(UsageEvent.cost_cents), 0),
        )
        .where(UsageEvent.created_at >= period_start)
        .where(UsageEvent.created_at < period_end)
        .group_by(UsageEvent.org_id)
    )
    count = 0
    for org_id, total_units, total_cost in result.all():
        invoice = Invoice(
            org_id=org_id,
            period_start=period_start,
            period_end=period_end,
            total_units=int(total_units),
            total_cost_cents=int(total_cost),
        )
        db.add(invoice)
        count += 1
    if count:
        await db.commit()
    return count


def month_bounds(dt: datetime) -> tuple[datetime, datetime]:
    start = datetime(dt.year, dt.month, 1, tzinfo=timezone.utc)
    if dt.month == 12:
        end = datetime(dt.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(dt.year, dt.month + 1, 1, tzinfo=timezone.utc)
    return start, end
