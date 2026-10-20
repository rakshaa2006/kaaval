"""Transactional task and Task Passport lifecycle operations."""
from __future__ import annotations

from sqlalchemy import event, inspect, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session

from app.api.errors import APIError
from app.audit.service import append_audit_event
from app.auth.service import AuthenticatedUser
from app.db.base import utc_now
from app.models import Task, TaskPassport
from app.services.passport_compiler import (
    compile_invoice_passport,
    passport_permissions_are_valid,
)

_IMMUTABLE_PASSPORT_FIELDS = (
    "task_id",
    "organization_id",
    "version",
    "passport_type",
    "generation_status",
    "allowed_tools_json",
    "forbidden_tools_json",
    "approval_rules_json",
    "data_constraints_json",
    "generation_metadata_json",
    "purpose",
    "expires_at",
    "activated_at",
    "created_at",
)
_PASSPORT_STATUS_TRANSITIONS = {
    "DRAFT": {"ACTIVE", "CANCELLED", "EXPIRED"},
    "ACTIVE": {"SUPERSEDED", "EXPIRED"},
}


@event.listens_for(Session, "before_flush")
def _reject_activated_passport_content_changes(
    session: Session,
    flush_context: object,
    instances: object,
) -> None:
    for passport in session.dirty:
        if not isinstance(passport, TaskPassport):
            continue
        state = inspect(passport)
        status_history = state.attrs.activation_status.history
        if status_history.has_changes() and status_history.deleted:
            previous_status = status_history.deleted[0]
            if (
                passport.activation_status != previous_status
                and passport.activation_status
                not in _PASSPORT_STATUS_TRANSITIONS.get(previous_status, set())
            ):
                raise ValueError(
                    f"Invalid Task Passport transition: {previous_status} "
                    f"to {passport.activation_status}."
                )
        activation_history = state.attrs.activated_at.history
        was_already_activated = (
            bool(activation_history.deleted)
            and activation_history.deleted[0] is not None
        ) or (
            not activation_history.has_changes() and passport.activated_at is not None
        )
        if was_already_activated and any(
            state.attrs[field].history.has_changes()
            for field in _IMMUTABLE_PASSPORT_FIELDS
        ):
            raise ValueError("Activated Task Passport contents cannot be changed.")


def get_scoped_task(
    db: Session,
    principal: AuthenticatedUser,
    task_id: str,
    *,
    for_update: bool = False,
) -> Task:
    statement = select(Task).where(
        Task.id == task_id,
        Task.organization_id == principal.organization_id,
        Task.owner_id == principal.user.id,
    )
    if for_update:
        statement = statement.with_for_update()
    task = db.scalar(statement)
    if task is None:
        raise APIError(404, "TASK_NOT_FOUND", "Task was not found.")
    return task


def get_latest_passport(
    db: Session, task: Task, *, for_update: bool = False
) -> TaskPassport | None:
    statement = (
        select(TaskPassport)
        .where(
            TaskPassport.task_id == task.id,
            TaskPassport.organization_id == task.organization_id,
        )
        .order_by(TaskPassport.version.desc())
        .limit(1)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def refresh_expiry(task: Task, latest_passport: TaskPassport | None) -> bool:
    if (
        latest_passport is None
        or latest_passport.expires_at is None
        or latest_passport.expires_at > utc_now()
        or latest_passport.activation_status not in ("DRAFT", "ACTIVE")
    ):
        return False
    latest_passport.activation_status = "EXPIRED"
    if task.status in ("PASSPORT_REVIEW", "ACTIVE"):
        task.status = "EXPIRED"
        task.updated_at = utc_now()
    return True


def create_task(db: Session, principal: AuthenticatedUser, purpose: str) -> Task:
    task = Task(
        organization_id=principal.organization_id,
        owner_id=principal.user.id,
        purpose=purpose,
        status="PASSPORT_GENERATING",
    )
    db.add(task)
    db.flush()
    append_audit_event(
        db,
        organization_id=principal.organization_id,
        task_id=task.id,
        actor_type="OWNER",
        actor_id=principal.user.id,
        event_type="TASK_CREATED",
        description="Invoice-summary task created.",
    )
    db.commit()
    return task


def generate_passport(
    db: Session,
    principal: AuthenticatedUser,
    task: Task,
    *,
    regenerate: bool,
) -> TaskPassport:
    latest = get_latest_passport(db, task, for_update=True)
    refresh_expiry(task, latest)
    if regenerate:
        if latest is None:
            raise APIError(
                409,
                "PASSPORT_NOT_GENERATED",
                "Generate an initial Passport before regenerating.",
            )
        if task.status not in ("PASSPORT_REVIEW", "ACTIVE", "EXPIRED"):
            raise APIError(
                409,
                "INVALID_TASK_STATE",
                "Passport cannot be regenerated in the current task state.",
            )
        if latest.activation_status == "DRAFT":
            latest.activation_status = "CANCELLED"
        version = latest.version + 1
        event_type = "PASSPORT_REGENERATED"
    else:
        if task.status != "PASSPORT_GENERATING" or latest is not None:
            raise APIError(
                409,
                "INVALID_TASK_STATE",
                "Initial Passport generation is not allowed in the current task state.",
            )
        version = 1
        event_type = "PASSPORT_GENERATED"

    try:
        passport = compile_invoice_passport(task, version)
    except ValueError as exc:
        raise APIError(422, "UNSUPPORTED_TASK_PURPOSE", str(exc)) from exc

    db.add(passport)
    task.status = "PASSPORT_REVIEW"
    task.updated_at = utc_now()
    db.flush()
    append_audit_event(
        db,
        organization_id=principal.organization_id,
        task_id=task.id,
        actor_type="OWNER",
        actor_id=principal.user.id,
        event_type=event_type,
        description=(
            f"Task Passport version {version} generated for owner review."
        ),
    )
    db.commit()
    return passport


def activate_passport(
    db: Session,
    principal: AuthenticatedUser,
    task: Task,
) -> TaskPassport:
    latest = get_latest_passport(db, task, for_update=True)
    if refresh_expiry(task, latest):
        db.commit()
    if task.status != "PASSPORT_REVIEW" or latest is None:
        raise APIError(
            409,
            "INVALID_TASK_STATE",
            "Task must have a reviewable Passport before activation.",
        )
    if (
        latest.activation_status != "DRAFT"
        or latest.generation_status != "GENERATED"
        or latest.expires_at is None
        or latest.expires_at <= utc_now()
    ):
        raise APIError(409, "INVALID_PASSPORT", "Passport is invalid or expired.")
    if not passport_permissions_are_valid(latest):
        raise APIError(
            409,
            "INVALID_PASSPORT_PERMISSIONS",
            "Passport permissions do not match the deterministic MVP policy.",
        )

    active_passports = db.scalars(
        select(TaskPassport).where(
            TaskPassport.task_id == task.id,
            TaskPassport.organization_id == principal.organization_id,
            TaskPassport.activation_status == "ACTIVE",
        )
    ).all()
    for previous in active_passports:
        previous.activation_status = "SUPERSEDED"

    latest.activation_status = "ACTIVE"
    latest.activated_at = utc_now()
    task.status = "ACTIVE"
    task.updated_at = utc_now()
    db.flush()
    append_audit_event(
        db,
        organization_id=principal.organization_id,
        task_id=task.id,
        actor_type="OWNER",
        actor_id=principal.user.id,
        event_type="PASSPORT_ACTIVATED",
        description=f"Task Passport version {latest.version} activated.",
    )
    db.commit()
    return latest
