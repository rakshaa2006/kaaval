"""Append-only persistence for audit events."""
from __future__ import annotations

from typing import Optional

from sqlalchemy import event
from sqlalchemy.orm import ORMExecuteState, Session

from app.models.audit_event import AuditEvent


def append_audit_event(
    db: Session,
    *,
    organization_id: str,
    event_type: str,
    actor_type: str,
    description: str,
    actor_id: Optional[str] = None,
    task_id: Optional[str] = None,
    session_id: Optional[str] = None,
    action_id: Optional[str] = None,
    incident_id: Optional[str] = None,
    approval_id: Optional[str] = None,
    metadata_json: Optional[str] = None,
    is_simulation: bool = False,
) -> AuditEvent:
    """Add an event to the caller's transaction without committing it."""
    audit_event = AuditEvent(
        organization_id=organization_id,
        event_type=event_type,
        actor_type=actor_type,
        actor_id=actor_id,
        task_id=task_id,
        session_id=session_id,
        action_id=action_id,
        incident_id=incident_id,
        approval_id=approval_id,
        description=description,
        metadata_json=metadata_json,
        is_simulation=is_simulation,
    )
    db.add(audit_event)
    return audit_event


@event.listens_for(Session, "before_flush")
def _reject_audit_mutations(
    session: Session,
    flush_context: object,
    instances: object,
) -> None:
    if any(isinstance(instance, AuditEvent) for instance in session.deleted):
        raise ValueError("Audit events cannot be deleted.")

    if any(
        isinstance(instance, AuditEvent) and session.is_modified(instance, include_collections=True)
        for instance in session.dirty
    ):
        raise ValueError("Audit events cannot be updated.")


@event.listens_for(Session, "do_orm_execute")
def _reject_bulk_audit_mutations(execute_state: ORMExecuteState) -> None:
    statement = execute_state.statement
    statement_table = getattr(statement, "table", None)
    if (
        statement_table is not None
        and statement_table.name == AuditEvent.__tablename__
        and (execute_state.is_update or execute_state.is_delete)
    ):
        raise ValueError("Audit events cannot be updated or deleted.")
