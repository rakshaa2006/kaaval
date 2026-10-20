"""Tests for demo and password authentication."""
from __future__ import annotations

import hashlib
from datetime import timedelta
from pathlib import Path

import pytest
from sqlalchemy import select

from app.config import AppEnv, Settings
from app.db.base import utc_now
from app.models import AuthSession, AuditEvent, Organization, User
from app.seed import (
    DEMO_OWNER_EMAIL,
    DEMO_OWNER_PASSWORD,
    seed_synthetic_data,
)

FIXTURE_DIRECTORY = Path(__file__).resolve().parents[2] / "fixtures" / "invoices"


def seed_owner(db_session) -> User:
    seed_synthetic_data(db_session, FIXTURE_DIRECTORY)
    return db_session.scalar(select(User).where(User.email == DEMO_OWNER_EMAIL))


def test_valid_demo_login_sets_http_only_cookie_and_audit(client, db_session) -> None:
    owner = seed_owner(db_session)

    result = client.post("/api/auth/demo-login")

    assert result.status_code == 200
    assert result.json()["user"]["id"] == owner.id
    assert result.json()["user"]["role"] == "OWNER_ADMIN"
    assert "kaaval_session" not in result.json()
    cookie = result.cookies.get("kaaval_session")
    assert cookie
    assert "httponly" in result.headers["set-cookie"].lower()
    stored_session = db_session.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == hashlib.sha256(cookie.encode()).hexdigest()
        )
    )
    assert stored_session is not None
    assert stored_session.token_hash != cookie
    assert stored_session.organization_id == owner.organization_id
    assert db_session.scalar(
        select(AuditEvent).where(AuditEvent.event_type == "DEMO_LOGIN")
    ) is not None


def test_valid_password_login_normalizes_email(client, db_session) -> None:
    owner = seed_owner(db_session)

    result = client.post(
        "/api/auth/login",
        json={"email": "  OWNER@EXAMPLE.TEST  ", "password": DEMO_OWNER_PASSWORD},
    )

    assert result.status_code == 200
    assert result.json()["user"]["email"] == DEMO_OWNER_EMAIL
    assert result.json()["user"]["organization_id"] == owner.organization_id
    assert result.cookies.get("kaaval_session")


def test_password_and_session_token_are_never_stored_in_plaintext(
    client, db_session
) -> None:
    owner = seed_owner(db_session)

    result = client.post(
        "/api/auth/login",
        json={"email": DEMO_OWNER_EMAIL, "password": DEMO_OWNER_PASSWORD},
    )

    token = result.cookies.get("kaaval_session")
    assert owner.password_hash != DEMO_OWNER_PASSWORD
    assert DEMO_OWNER_PASSWORD not in owner.password_hash
    assert token
    assert token not in result.text
    assert db_session.scalar(
        select(AuthSession).where(AuthSession.token_hash == token)
    ) is None
    assert db_session.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == hashlib.sha256(token.encode()).hexdigest()
        )
    ) is not None


@pytest.mark.parametrize(
    ("email", "password"),
    [
        (DEMO_OWNER_EMAIL, "not-the-demo-password"),
        ("unknown@example.test", DEMO_OWNER_PASSWORD),
    ],
)
def test_invalid_password_or_unknown_email_is_rejected(client, db_session, email, password):
    seed_owner(db_session)

    result = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )

    assert result.status_code == 401
    assert result.json()["code"] == "INVALID_CREDENTIALS"
    assert result.cookies.get("kaaval_session") is None


def test_inactive_user_cannot_log_in(client, db_session) -> None:
    owner = seed_owner(db_session)
    owner.status = "DISABLED"
    db_session.flush()

    result = client.post(
        "/api/auth/login",
        json={"email": DEMO_OWNER_EMAIL, "password": DEMO_OWNER_PASSWORD},
    )

    assert result.status_code == 401
    assert result.json()["code"] == "INVALID_CREDENTIALS"


def test_me_uses_authenticated_user_and_organization_scope(client, db_session) -> None:
    owner = seed_owner(db_session)
    other_organization = Organization(
        name="Synthetic Other Organization",
        environment="SYNTHETIC_DEMO",
        is_active=True,
    )
    db_session.add(other_organization)
    db_session.flush()
    assert other_organization.id != owner.organization_id

    login_result = client.post(
        "/api/auth/login",
        json={"email": DEMO_OWNER_EMAIL, "password": DEMO_OWNER_PASSWORD},
    )
    result = client.get("/api/auth/me")

    assert login_result.status_code == 200
    assert result.status_code == 200
    assert result.json()["id"] == owner.id
    assert result.json()["organization_id"] == owner.organization_id
    assert result.json()["organization_id"] != other_organization.id


def test_authenticated_user_can_be_loaded_from_bearer_token(client, db_session) -> None:
    owner = seed_owner(db_session)
    login_result = client.post(
        "/api/auth/login",
        json={"email": DEMO_OWNER_EMAIL, "password": DEMO_OWNER_PASSWORD},
    )
    token = login_result.cookies.get("kaaval_session")

    result = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert result.status_code == 200
    assert result.json()["id"] == owner.id


def test_login_rejects_client_supplied_identity_and_role(client, db_session) -> None:
    seed_owner(db_session)

    result = client.post(
        "/api/auth/login",
        json={
            "email": DEMO_OWNER_EMAIL,
            "password": DEMO_OWNER_PASSWORD,
            "organization_id": "attacker-organization",
            "user_id": "attacker-user",
            "role": "OWNER_ADMIN",
        },
    )

    assert result.status_code == 422
    assert result.json()["code"] == "VALIDATION_ERROR"
    assert "password" not in result.text
    assert result.cookies.get("kaaval_session") is None


def test_expired_session_is_rejected(client, db_session) -> None:
    seed_owner(db_session)
    login_result = client.post("/api/auth/demo-login")
    token = login_result.cookies.get("kaaval_session")
    auth_session = db_session.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == hashlib.sha256(token.encode()).hexdigest()
        )
    )
    assert auth_session is not None
    auth_session.expires_at = utc_now() - timedelta(seconds=1)
    db_session.flush()

    result = client.get("/api/auth/me")

    assert result.status_code == 401
    assert result.json()["code"] == "UNAUTHENTICATED"


def test_revoked_session_is_rejected(client, db_session) -> None:
    seed_owner(db_session)
    login_result = client.post("/api/auth/demo-login")
    token = login_result.cookies.get("kaaval_session")
    auth_session = db_session.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == hashlib.sha256(token.encode()).hexdigest()
        )
    )
    assert auth_session is not None
    auth_session.revoked_at = utc_now()
    db_session.flush()

    result = client.get("/api/auth/me")

    assert result.status_code == 401
    assert result.json()["code"] == "UNAUTHENTICATED"


def test_logout_revokes_session_and_clears_cookie(client, db_session) -> None:
    owner = seed_owner(db_session)
    login_result = client.post("/api/auth/demo-login")
    assert login_result.status_code == 200
    authenticated_result = client.get("/api/auth/me")
    assert authenticated_result.status_code == 200
    assert authenticated_result.json()["id"] == owner.id

    token = login_result.cookies.get("kaaval_session")
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    logout_result = client.post("/api/auth/logout")

    assert logout_result.status_code == 200
    assert logout_result.json() == {"status": "logged_out"}
    assert client.get("/api/auth/me").status_code == 401
    auth_session = db_session.scalar(
        select(AuthSession).where(AuthSession.token_hash == token_hash)
    )
    assert auth_session is not None
    assert auth_session.revoked_at is not None
    assert db_session.scalar(
        select(AuditEvent).where(AuditEvent.event_type == "LOGOUT")
    ) is not None


@pytest.mark.parametrize("environment", [AppEnv.STAGING, AppEnv.PRODUCTION])
def test_demo_login_is_rejected_outside_synthetic_environment(
    client, monkeypatch, environment
) -> None:
    monkeypatch.setattr(
        "app.api.auth.get_settings",
        lambda: Settings(app_env=environment),
    )

    result = client.post("/api/auth/demo-login")

    assert result.status_code == 403
    assert result.json()["code"] == "DEMO_LOGIN_DISABLED"


def test_auth_me_rejects_missing_session(client) -> None:
    result = client.get("/api/auth/me")

    assert result.status_code == 401
    assert result.json()["code"] == "UNAUTHENTICATED"
