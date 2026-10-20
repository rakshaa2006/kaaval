"""Authenticated task and Task Passport lifecycle endpoints."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import APIError
from app.audit.service import append_audit_event
from app.auth.service import AuthenticatedUser, get_authenticated_user, get_session_token
from app.db.base import get_db, utc_now
from app.models import AgentSession, Task, TaskPassport
from app.schemas.tasks import (
    AgentSessionResponse,
    PassportDataPolicy,
    PassportResponse,
    TaskCreateRequest,
    TaskResponse,
)
from app.services.passport_compiler import passport_permissions_are_valid
from app.services.task_lifecycle import (
    activate_passport,
    create_task,
    generate_passport,
    get_latest_passport,
    get_scoped_task,
    refresh_expiry,
)

router = APIRouter(prefix="/tasks", tags=["tasks and passports"])


def _require_principal(request: Request, db: Session) -> AuthenticatedUser:
    principal = get_authenticated_user(db, get_session_token(request))
    if principal is None:
        raise APIError(401, "UNAUTHENTICATED", "Authentication is required.")
    return principal


def _task_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        organization_id=task.organization_id,
        owner_id=task.owner_id,
        purpose=task.purpose,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def _passport_response(passport: TaskPassport) -> PassportResponse:
    if passport.expires_at is None or not passport_permissions_are_valid(passport):
        raise APIError(
            409,
            "INVALID_PASSPORT",
            "Passport contents do not match the deterministic MVP policy.",
        )
    return PassportResponse(
        id=passport.id,
        task_id=passport.task_id,
        organization_id=passport.organization_id,
        version=passport.version,
        passport_type=passport.passport_type,
        generation_status=passport.generation_status,
        activation_status=passport.activation_status,
        purpose=passport.purpose,
        allowed_tools=json.loads(passport.allowed_tools_json),
        approval_required_tools=json.loads(passport.approval_rules_json),
        forbidden_tools=json.loads(passport.forbidden_tools_json),
        data_policy=PassportDataPolicy.model_validate(
            json.loads(passport.data_constraints_json)
        ),
        expires_at=passport.expires_at,
        activated_at=passport.activated_at,
        created_at=passport.created_at,
    )


def _session_response(agent_session: AgentSession) -> AgentSessionResponse:
    return AgentSessionResponse(
        id=agent_session.id,
        organization_id=agent_session.organization_id,
        task_id=agent_session.task_id,
        passport_id=agent_session.passport_id,
        owner_id=agent_session.owner_id,
        status=agent_session.status,
        created_at=agent_session.created_at,
    )


@router.post("", response_model=TaskResponse, status_code=201)
def create_task_endpoint(
    payload: TaskCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TaskResponse:
    principal = _require_principal(request, db)
    return _task_response(create_task(db, principal, payload.purpose))


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_endpoint(
    task_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> TaskResponse:
    principal = _require_principal(request, db)
    task = get_scoped_task(db, principal, task_id)
    if refresh_expiry(task, get_latest_passport(db, task)):
        db.commit()
    return _task_response(task)


@router.post("/{task_id}/passport/generate", response_model=PassportResponse)
def generate_passport_endpoint(
    task_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> PassportResponse:
    principal = _require_principal(request, db)
    task = get_scoped_task(db, principal, task_id, for_update=True)
    return _passport_response(
        generate_passport(db, principal, task, regenerate=False)
    )


@router.get("/{task_id}/passport", response_model=PassportResponse)
def get_passport_endpoint(
    task_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> PassportResponse:
    principal = _require_principal(request, db)
    task = get_scoped_task(db, principal, task_id)
    passport = get_latest_passport(db, task)
    if passport is None:
        raise APIError(404, "PASSPORT_NOT_FOUND", "Task Passport was not found.")
    if refresh_expiry(task, passport):
        db.commit()
    return _passport_response(passport)


@router.post("/{task_id}/passport/activate", response_model=PassportResponse)
def activate_passport_endpoint(
    task_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> PassportResponse:
    principal = _require_principal(request, db)
    task = get_scoped_task(db, principal, task_id, for_update=True)
    return _passport_response(activate_passport(db, principal, task))


@router.post("/{task_id}/passport/regenerate", response_model=PassportResponse)
def regenerate_passport_endpoint(
    task_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> PassportResponse:
    principal = _require_principal(request, db)
    task = get_scoped_task(db, principal, task_id, for_update=True)
    return _passport_response(
        generate_passport(db, principal, task, regenerate=True)
    )


@router.post(
    "/{task_id}/sessions",
    response_model=AgentSessionResponse,
    status_code=201,
)
def create_session_endpoint(
    task_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> AgentSessionResponse:
    principal = _require_principal(request, db)
    task = get_scoped_task(db, principal, task_id, for_update=True)
    if task.status != "ACTIVE":
        raise APIError(
            409,
            "TASK_NOT_ACTIVE",
            "Task must be active before a session can be created.",
        )

    passport = db.scalar(
        select(TaskPassport)
        .where(
            TaskPassport.task_id == task.id,
            TaskPassport.organization_id == principal.organization_id,
            TaskPassport.activation_status == "ACTIVE",
        )
        .order_by(TaskPassport.version.desc())
        .with_for_update()
    )
    if passport is None:
        raise APIError(
            409,
            "ACTIVE_PASSPORT_REQUIRED",
            "Task must have an active Passport before a session can be created.",
        )
    if not passport.is_active_and_valid:
        if passport.activation_status == "ACTIVE" and (
            passport.expires_at is None or passport.expires_at <= utc_now()
        ):
            passport.activation_status = "EXPIRED"
            task.status = "EXPIRED"
            task.updated_at = utc_now()
            db.commit()
        raise APIError(
            409,
            "ACTIVE_PASSPORT_REQUIRED",
            "Task Passport must be active and unexpired before session creation.",
        )
    if passport.generation_status != "GENERATED" or not passport_permissions_are_valid(
        passport
    ):
        raise APIError(
            409,
            "INVALID_PASSPORT",
            "Task Passport policy could not be verified.",
        )

    agent_session = AgentSession(
        organization_id=principal.organization_id,
        task_id=task.id,
        passport_id=passport.id,
        owner_id=principal.user.id,
        status="ACTIVE",
    )
    db.add(agent_session)
    db.flush()
    append_audit_event(
        db,
        organization_id=principal.organization_id,
        task_id=task.id,
        session_id=agent_session.id,
        actor_type="OWNER",
        actor_id=principal.user.id,
        event_type="SESSION_CREATED",
        description="Active agent session created for the task.",
        is_simulation=True,
    )
    db.commit()
    return _session_response(agent_session)
