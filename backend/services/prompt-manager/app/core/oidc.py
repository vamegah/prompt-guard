from dataclasses import dataclass
from typing import Any, Dict
import uuid

import jwt
from jwt import PyJWKClient
from fastapi import Header, HTTPException

from app.core.config import settings


@dataclass
class Principal:
    user_id: Any
    org_id: Any
    claims: Dict[str, Any]


def _get_jwks_client() -> PyJWKClient:
    if not settings.OIDC_JWKS_URL:
        raise HTTPException(status_code=500, detail="OIDC JWKS URL not configured")
    return PyJWKClient(settings.OIDC_JWKS_URL)


def _maybe_uuid(value: str | None) -> Any:
    if not value:
        return value
    try:
        return uuid.UUID(value)
    except (ValueError, TypeError):
        return value


def get_current_principal(
    authorization: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_org_id: str | None = Header(default=None, alias="X-Org-Id"),
    x_role: str | None = Header(default=None, alias="X-Role"),
) -> Principal:
    if bool(settings.OIDC_ENABLED):
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Missing bearer token")
        token = authorization.split(" ", 1)[1]
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        try:
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=settings.OIDC_ALLOWED_ALGS,
                audience=settings.OIDC_AUDIENCE,
                issuer=settings.OIDC_ISSUER,
            )
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = str(claims.get("sub"))
        org_id = str(claims.get("org_id") or claims.get("org"))
        if not user_id or not org_id:
            raise HTTPException(status_code=403, detail="Missing subject/org in token")
        return Principal(
            user_id=_maybe_uuid(user_id),
            org_id=_maybe_uuid(org_id),
            claims=claims,
        )

    if not x_user_id or not x_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return Principal(
        user_id=_maybe_uuid(x_user_id),
        org_id=_maybe_uuid(x_org_id),
        claims={"role": x_role} if x_role else {},
    )
