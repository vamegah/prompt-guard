from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.security import verify_api_key, role_required
from app.core.secrets import encrypt_value, decrypt_value, rewrap_value, rotate_backend_key, SecretsError
from app.core.audit import log_action
from app.db.session import get_db
from app.models import Organization, User, Role, Membership, LLMApiKey


router = APIRouter(
    dependencies=[Depends(verify_api_key), Depends(role_required("admin"))]
)


@router.post("/orgs")
async def create_org(
    name: str,
    db: AsyncSession = Depends(get_db),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    org = Organization(name=name)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    await log_action(db, x_actor or "system", "create", "organization", str(org.id))
    return {"id": org.id, "name": org.name}


@router.post("/users")
async def create_user(
    email: str,
    name: str | None = None,
    db: AsyncSession = Depends(get_db),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    user = User(email=email, name=name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await log_action(db, x_actor or "system", "create", "user", str(user.id))
    return {"id": user.id, "email": user.email, "name": user.name}


@router.post("/roles")
async def create_role(
    name: str,
    db: AsyncSession = Depends(get_db),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    role = Role(name=name)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    await log_action(db, x_actor or "system", "create", "role", str(role.id))
    return {"id": role.id, "name": role.name}


@router.post("/memberships")
async def create_membership(
    user_id: UUID,
    org_id: UUID,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    membership = Membership(user_id=user_id, org_id=org_id, role_id=role_id)
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    await log_action(db, x_actor or "system", "create", "membership", str(membership.id))
    return {"id": membership.id}


@router.post("/api-keys")
async def create_api_key(
    org_id: UUID,
    provider: str,
    name: str,
    value: str,
    db: AsyncSession = Depends(get_db),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    encrypted = encrypt_value(value)
    entry = LLMApiKey(
        org_id=org_id, provider=provider, name=name, encrypted_value=encrypted
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    await log_action(db, x_actor or "system", "create", "api_key", str(entry.id))
    return {"id": entry.id, "provider": provider, "name": name}


@router.get("/api-keys", response_model=List[dict])
async def list_api_keys(
    org_id: UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(LLMApiKey).where(LLMApiKey.org_id == org_id))
    items = result.scalars().all()
    return [
        {
            "id": item.id,
            "provider": item.provider,
            "name": item.name,
            "last_rotated_at": item.last_rotated_at,
        }
        for item in items
    ]


@router.post("/api-keys/{key_id}/rotate")
async def rotate_api_key(
    key_id: UUID,
    value: str,
    db: AsyncSession = Depends(get_db),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    entry = await db.get(LLMApiKey, key_id)
    if not entry:
        raise HTTPException(status_code=404, detail="API key not found")
    entry.encrypted_value = encrypt_value(value)
    await db.commit()
    await db.refresh(entry)
    await log_action(db, x_actor or "system", "rotate", "api_key", str(entry.id))
    return {"id": entry.id}


@router.post("/api-keys/rewrap")
async def rewrap_api_keys(
    org_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    try:
        stmt = select(LLMApiKey)
        if org_id:
            stmt = stmt.where(LLMApiKey.org_id == org_id)
        result = await db.execute(stmt)
        items = result.scalars().all()
        for entry in items:
            entry.encrypted_value = rewrap_value(entry.encrypted_value)
        await db.commit()
        await log_action(db, x_actor or "system", "rewrap", "api_key", str(org_id) if org_id else "all")
        return {"rewrapped": len(items)}
    except SecretsError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/secrets/rotate")
async def rotate_secret_backend(
    db: AsyncSession = Depends(get_db),
    x_actor: str | None = Header(default="system", alias="X-Actor"),
):
    try:
        rotate_backend_key()
        await log_action(db, x_actor or "system", "rotate", "secret_backend", "default")
        return {"status": "rotated"}
    except SecretsError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/api-keys/{key_id}/reveal")
async def reveal_api_key(
    key_id: UUID, db: AsyncSession = Depends(get_db)
):
    entry = await db.get(LLMApiKey, key_id)
    if not entry:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"id": entry.id, "value": decrypt_value(entry.encrypted_value)}
