"""Authentication endpoints for synthetic demo and password login."""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.errors import APIError
from app.audit.service import append_audit_event
from app.auth.service import (
    SESSION_COOKIE_NAME,
    AuthenticatedUser,
    authenticate_password,
    create_browser_session,
    get_authenticated_user,
    get_session_token,
    user_is_active,
)
from app.config import AppEnv, get_settings
from app.db.base import get_db, utc_now
from app.models import Organization, User
from app.seed import DEMO_OWNER_EMAIL
from app.schemas.auth import (
    AuthenticatedUserResponse,
    AuthResponse,
    LoginRequest,
    LogoutResponse,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def _user_response(user: User) -> AuthenticatedUserResponse:
    return AuthenticatedUserResponse(
        id=user.id,
        organization_id=user.organization_id,
        organization_name=user.organization.name,
        email=user.email,
        role=user.role,
        status=user.status,
    )


def _set_session_cookie(response: Response, token: str, expires_at: datetime) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=max(0, int((expires_at - utc_now()).total_seconds())),
        httponly=True,
        secure=get_settings().app_env != AppEnv.SYNTHETIC_DEMO,
        samesite="lax",
        path="/",
    )


def _authenticated_principal(
    request: Request,
    db: Session,
) -> AuthenticatedUser:
    principal = get_authenticated_user(db, get_session_token(request))
    if principal is None:
        raise APIError(401, "UNAUTHENTICATED", "Authentication is required.")
    return principal


def _record_login(db: Session, user: User, event_type: str) -> tuple[AuthResponse, str]:
    auth_session, raw_token = create_browser_session(db, user)
    append_audit_event(
        db,
        organization_id=user.organization_id,
        event_type=event_type,
        actor_type="OWNER",
        actor_id=user.id,
        description="User authenticated successfully.",
    )
    db.commit()
    return (
        AuthResponse(user=_user_response(user), expires_at=auth_session.expires_at),
        raw_token,
    )


@router.post("/demo-login", response_model=AuthResponse)
def demo_login(response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    if get_settings().app_env != AppEnv.SYNTHETIC_DEMO:
        raise APIError(
            403,
            "DEMO_LOGIN_DISABLED",
            "Demo login is available only in the synthetic demo environment.",
        )

    user = db.scalar(
        select(User)
        .options(joinedload(User.organization))
        .where(
            User.email == DEMO_OWNER_EMAIL,
            User.role == "OWNER_ADMIN",
            User.organization.has(Organization.environment == AppEnv.SYNTHETIC_DEMO.value),
        )
    )
    if user is None or not user_is_active(user):
        raise APIError(401, "UNAUTHENTICATED", "Demo account is unavailable.")

    auth_response, token = _record_login(db, user, "DEMO_LOGIN")
    _set_session_cookie(response, token, auth_response.expires_at)
    return auth_response


@router.post("/login", response_model=AuthResponse)
def login(
    credentials: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user = authenticate_password(db, credentials.email, credentials.password)
    if user is None:
        raise APIError(401, "INVALID_CREDENTIALS", "Email or password is incorrect.")

    auth_response, token = _record_login(db, user, "LOGIN")
    _set_session_cookie(response, token, auth_response.expires_at)
    return auth_response


@router.post("/logout", response_model=LogoutResponse)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> LogoutResponse:
    principal = _authenticated_principal(request, db)
    principal.auth_session.revoked_at = datetime.now(UTC).replace(tzinfo=None)
    append_audit_event(
        db,
        organization_id=principal.organization_id,
        event_type="LOGOUT",
        actor_type="OWNER",
        actor_id=principal.user.id,
        description="User logged out and session was revoked.",
    )
    db.commit()
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        secure=get_settings().app_env != AppEnv.SYNTHETIC_DEMO,
        samesite="lax",
        path="/",
    )
    return LogoutResponse()


@router.get("/me", response_model=AuthenticatedUserResponse)
def me(request: Request, db: Session = Depends(get_db)) -> AuthenticatedUserResponse:
    principal = _authenticated_principal(request, db)
    return _user_response(principal.user)
