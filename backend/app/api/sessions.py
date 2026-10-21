"""Authenticated session inspection and timeline endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import APIError
from app.auth.service import (
    AuthenticatedUser,
    get_authenticated_user,
    get_session_token,
)
from app.db.base import get_db
from app.models import AgentSession, AuditEvent
from app.schemas.audit import AuditEventResponse
from app.schemas.tasks import AgentSessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _get_scoped_session(
    db: Session,
    principal: AuthenticatedUser,
    session_id: str,
) -> AgentSession:
    agent_session = db.scalar(
        select(AgentSession).where(
            AgentSession.id == session_id,
            AgentSession.organization_id == principal.organization_id,
            AgentSession.owner_id == principal.user.id,
        )
    )
    if agent_session is None:
        raise APIError(404, "SESSION_NOT_FOUND", "Session was not found.")
    return agent_session


@router.get("", response_model=list[AgentSessionResponse])
def list_sessions(
    request: Request,
    db: Session = Depends(get_db),
) -> list[AgentSessionResponse]:
    principal = get_authenticated_user(db, get_session_token(request))
    if principal is None:
        raise APIError(401, "UNAUTHENTICATED", "Authentication is required.")
    sessions = db.scalars(
        select(AgentSession)
        .where(
            AgentSession.organization_id == principal.organization_id,
            AgentSession.owner_id == principal.user.id,
        )
        .order_by(AgentSession.created_at.desc())
    ).all()
    return [
        AgentSessionResponse(
            id=agent_session.id,
            organization_id=agent_session.organization_id,
            task_id=agent_session.task_id,
            passport_id=agent_session.passport_id,
            owner_id=agent_session.owner_id,
            status=agent_session.status,
            created_at=agent_session.created_at,
        )
        for agent_session in sessions
    ]


@router.get("/{session_id}", response_model=AgentSessionResponse)
def get_session(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> AgentSessionResponse:
    principal = get_authenticated_user(db, get_session_token(request))
    if principal is None:
        raise APIError(401, "UNAUTHENTICATED", "Authentication is required.")
    agent_session = _get_scoped_session(db, principal, session_id)
    return AgentSessionResponse(
        id=agent_session.id,
        organization_id=agent_session.organization_id,
        task_id=agent_session.task_id,
        passport_id=agent_session.passport_id,
        owner_id=agent_session.owner_id,
        status=agent_session.status,
        created_at=agent_session.created_at,
    )


@router.get(
    "/{session_id}/timeline",
    response_model=list[AuditEventResponse],
)
def get_session_timeline(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> list[AuditEventResponse]:
    principal = get_authenticated_user(db, get_session_token(request))
    if principal is None:
        raise APIError(401, "UNAUTHENTICATED", "Authentication is required.")
    agent_session = _get_scoped_session(db, principal, session_id)
    events = db.scalars(
        select(AuditEvent)
        .where(
            AuditEvent.organization_id == principal.organization_id,
            AuditEvent.session_id == agent_session.id,
        )
        .order_by(AuditEvent.sequence.asc())
    ).all()
    return [AuditEventResponse.model_validate(event) for event in events]
