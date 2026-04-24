import time
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.oidc import get_current_principal, Principal
from app.db.session import get_db
from app.models import Membership, Role


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.API_KEY:
        return
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


def verify_internal_key(x_internal_key: str | None = Header(default=None, alias="X-Internal-Key")) -> None:
    if not settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=500, detail="Internal API key not configured")
    if not x_internal_key or x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def require_role(
    role: str,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> None:
    role_hierarchy = {
        "viewer": {"viewer", "editor", "admin"},
        "editor": {"editor", "admin"},
        "admin": {"admin"},
    }
    allowed_roles = role_hierarchy.get(role, {role})

    if not settings.OIDC_ENABLED:
        header_role = principal.claims.get("role") if principal.claims else None
        if header_role and header_role in allowed_roles:
            return

    stmt = (
        select(Membership)
        .join(Role, Membership.role_id == Role.id)
        .where(Membership.user_id == principal.user_id)
        .where(Membership.org_id == principal.org_id)
        .where(Role.name.in_(allowed_roles))
    )
    result = await db.execute(stmt)
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=403, detail="Forbidden")


def role_required(role: str):
    async def _dep(principal: Principal = Depends(get_current_principal), db: AsyncSession = Depends(get_db)) -> None:
        await require_role(role, principal, db)

    return _dep


def now_ms() -> int:
    return int(time.time() * 1000)
