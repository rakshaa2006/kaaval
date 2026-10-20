"""Incident containment and owner-review operations."""
from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import APIError
from app.audit.service import append_audit_event
from app.auth.service import AuthenticatedUser
from app.db.base import utc_now
from app.models import (
    ActionRequest,
    AgentSession,
    DataFinding,
    Incident,
    Notification,
)


def quarantine_session_for_action(
    db: Session,
    *,
    principal: AuthenticatedUser,
    agent_session: AgentSession,
    action: ActionRequest,
    findings: list[DataFinding],
) -> Incident | None:
    """Quarantine the active session and persist an incident and mock alert."""
    if agent_session.status == "QUARANTINED":
        return db.scalar(
            select(Incident)
            .where(
                Incident.agent_session_id == agent_session.id,
                Incident.triggering_action_id == action.id,
            )
            .order_by(Incident.created_at.desc())
        )
    if agent_session.status != "ACTIVE":
        return None

    categories = sorted({finding.category for finding in findings})
    agent_session.status = "QUARANTINED"
    agent_session.quarantine_reason = "SEVERE_UNSAFE_ACTION"
    agent_session.quarantined_at = utc_now()
    agent_session.updated_at = utc_now()

    incident = Incident(
        organization_id=principal.organization_id,
        agent_session_id=agent_session.id,
        triggering_action_id=action.id,
        severity="CRITICAL" if "DESTRUCTIVE_ACTION_REQUEST" in categories else "HIGH",
        summary="Kaaval contained a severe unsafe action. Review the masked findings.",
        containment_status="CONTAINED",
        owner_review_status="OPEN",
        recovery_status="NOT_STARTED",
    )
    db.add(incident)
    db.flush()

    notification = Notification(
        organization_id=principal.organization_id,
        incident_id=incident.id,
        notification_type="EMERGENCY_ALERT",
        channel="MOCK",
        status="PENDING",
        attempt_count=0,
    )
    db.add(notification)
    append_audit_event(
        db,
        organization_id=principal.organization_id,
        task_id=action.task_id,
        session_id=agent_session.id,
        action_id=action.id,
        incident_id=incident.id,
        actor_type="SYSTEM",
        event_type="SESSION_QUARANTINED",
        description="Session quarantined after a severe unsafe action.",
        metadata_json='{"reason_code":"SEVERE_UNSAFE_ACTION"}',
        is_simulation=True,
    )
    append_audit_event(
        db,
        organization_id=principal.organization_id,
        task_id=action.task_id,
        session_id=agent_session.id,
        action_id=action.id,
        incident_id=incident.id,
        actor_type="SYSTEM",
        event_type="INCIDENT_CREATED",
        description="An incident was created for a contained unsafe action.",
        metadata_json=json.dumps(
            {"finding_categories": categories}, separators=(",", ":"), sort_keys=True
        ),
        is_simulation=True,
    )
    append_audit_event(
        db,
        organization_id=principal.organization_id,
        task_id=action.task_id,
        session_id=agent_session.id,
        action_id=action.id,
        incident_id=incident.id,
        actor_type="SYSTEM",
        event_type="NOTIFICATION_QUEUED",
        description="A mock emergency notification intent was queued.",
        metadata_json='{"channel":"MOCK","notification_type":"EMERGENCY_ALERT"}',
        is_simulation=True,
    )
    return incident


def get_scoped_incident(
    db: Session, principal: AuthenticatedUser, incident_id: str
) -> Incident:
    incident = db.scalar(
        select(Incident).where(
            Incident.id == incident_id,
            Incident.organization_id == principal.organization_id,
        )
    )
    if incident is None:
        raise APIError(404, "INCIDENT_NOT_FOUND", "Incident was not found.")
    return incident


def acknowledge_incident(
    db: Session, principal: AuthenticatedUser, incident: Incident
) -> Incident:
    if incident.owner_review_status == "RESOLVED":
        raise APIError(409, "INCIDENT_RESOLVED", "Resolved incidents cannot be acknowledged.")
    if incident.owner_review_status == "OPEN":
        incident.owner_review_status = "REVIEWED"
        incident.updated_at = utc_now()
        append_audit_event(
            db,
            organization_id=principal.organization_id,
            session_id=incident.agent_session_id,
            incident_id=incident.id,
            actor_type="OWNER",
            actor_id=principal.user.id,
            event_type="INCIDENT_ACKNOWLEDGED",
            description="Owner acknowledged the contained incident.",
            is_simulation=True,
        )
        db.commit()
    return incident


def resolve_incident(
    db: Session, principal: AuthenticatedUser, incident: Incident
) -> Incident:
    if incident.owner_review_status != "RESOLVED":
        incident.owner_review_status = "RESOLVED"
        incident.resolved_at = utc_now()
        incident.updated_at = incident.resolved_at
        append_audit_event(
            db,
            organization_id=principal.organization_id,
            session_id=incident.agent_session_id,
            incident_id=incident.id,
            actor_type="OWNER",
            actor_id=principal.user.id,
            event_type="INCIDENT_RESOLVED",
            description="Owner resolved the incident; session remains quarantined.",
            is_simulation=True,
        )
        db.commit()
    return incident
