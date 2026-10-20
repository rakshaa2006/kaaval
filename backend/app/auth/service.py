"""Browser authentication and session helpers."""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.auth.security import verify_password
from app.config import get_settings
from app.db.base import utc_now
from app.models import AuthSession, User

SESSION_COOKIE_NAME = "kaaval_session"


@dataclass(frozen=True)
class AuthenticatedUser:
    user: User
    organization_id: str
    organization_name: str
    auth_session: AuthSession


def normalize_email(email: str) -> str:
    return email.strip().lower()


def user_is_active(user: User) -> bool:
    return user.status == "ACTIVE" and user.is_active and user.organization.is_active


def create_browser_session(db: Session, user: User) -> tuple[AuthSession, str]:
    token = secrets.token_urlsafe(32)
    now = utc_now()
    expires_at = now + timedelta(hours=get_settings().session_expire_hours)
    auth_session = AuthSession(
        user_id=user.id,
        organization_id=user.organization_id,
        token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
        created_at=now,
        last_seen_at=now,
        expires_at=expires_at,
    )
    db.add(auth_session)
    db.flush()
    return auth_session, token


def authenticate_password(db: Session, email: str, password: str) -> Optional[User]:
    user = db.scalar(
        select(User)
        .options(joinedload(User.organization))
        .where(User.email == normalize_email(email))
    )
    if user is None or not verify_password(password, user.password_hash):
        return None
    if not user_is_active(user):
        return None
    return user


def get_session_token(request: Request) -> Optional[str]:
    authorization = request.headers.get("authorization", "")
    scheme, separator, token = authorization.partition(" ")
    if separator and scheme.lower() == "bearer" and token.strip():
        return token.strip()
    return request.cookies.get(SESSION_COOKIE_NAME)


def get_authenticated_user(db: Session, token: Optional[str]) -> Optional[AuthenticatedUser]:
    if not token:
        return None
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    auth_session = db.scalar(
        select(AuthSession)
        .options(joinedload(AuthSession.user).joinedload(User.organization))
        .where(AuthSession.token_hash == token_hash)
    )
    if auth_session is None:
        return None
    now = utc_now()
    user = auth_session.user
    if auth_session.revoked_at is not None or auth_session.expires_at <= now:
        return None
    if not user_is_active(user):
        return None
    return AuthenticatedUser(
        user=user,
        organization_id=user.organization_id,
        organization_name=user.organization.name,
        auth_session=auth_session,
    )
