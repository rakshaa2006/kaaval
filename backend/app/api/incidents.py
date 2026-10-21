"""Organization-scoped incident review endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import APIError
from app.auth.service import AuthenticatedUser, get_authenticated_user, get_session_token
from app.db.base import get_db
from app.models import DataFinding, Incident, Notification
from app.schemas.privacy import (
    IncidentDetailResponse,
    IncidentSummaryResponse,
    NotificationResponse,
    PrivacyFindingResponse,
)
from app.services.incident_service import (
    acknowledge_incident,
    get_scoped_incident,
    resolve_incident,
)

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _require_owner(request: Request, db: Session) -> AuthenticatedUser:
    principal = get_authenticated_user(db, get_session_token(request))
    if principal is None:
        raise APIError(401, "UNAUTHENTICATED", "Authentication is required.")
    if principal.user.role != "OWNER_ADMIN":
        raise APIError(403, "FORBIDDEN", "Owner permissions are required.")
    return principal


def _summary(incident: Incident) -> IncidentSummaryResponse:
    return IncidentSummaryResponse(
        id=incident.id,
        organization_id=incident.organization_id,
        agent_session_id=incident.agent_session_id,
        task_id=incident.agent_session.task_id,
        triggering_action_id=incident.triggering_action_id,
        severity=incident.severity,
        summary=incident.summary,
        containment_status=incident.containment_status,
        owner_review_status=incident.owner_review_status,
        recovery_status=incident.recovery_status,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        resolved_at=incident.resolved_at,
    )


def _detail(db: Session, incident: Incident) -> IncidentDetailResponse:
    response = _summary(incident).model_dump()
    findings: list[PrivacyFindingResponse] = []
    if incident.triggering_action_id is not None:
        persisted_findings = db.scalars(
            select(DataFinding)
            .where(
                DataFinding.action_request_id == incident.triggering_action_id,
                DataFinding.organization_id == incident.organization_id,
            )
            .order_by(DataFinding.created_at)
        ).all()
        findings = [
            PrivacyFindingResponse(
                category=finding.category,
                masked_value=finding.masked_value,
                location_hint=finding.location_hint,
                confidence=finding.confidence,
            )
            for finding in persisted_findings
        ]
    notifications = db.scalars(
        select(Notification)
        .where(
            Notification.incident_id == incident.id,
            Notification.organization_id == incident.organization_id,
        )
        .order_by(Notification.created_at)
    ).all()
    response["findings"] = findings
    response["notifications"] = [
        NotificationResponse(
            id=notification.id,
            notification_type=notification.notification_type,
            channel=notification.channel,
            status=notification.status,
            created_at=notification.created_at,
        )
        for notification in notifications
    ]
    return IncidentDetailResponse.model_validate(response)


@router.get("", response_model=list[IncidentSummaryResponse])
def list_incidents(
    request: Request,
    db: Session = Depends(get_db),
) -> list[IncidentSummaryResponse]:
    principal = _require_owner(request, db)
    incidents = db.scalars(
        select(Incident)
        .where(Incident.organization_id == principal.organization_id)
        .order_by(Incident.created_at.desc())
    ).all()
    return [_summary(incident) for incident in incidents]


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident(
    incident_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> IncidentDetailResponse:
    principal = _require_owner(request, db)
    incident = get_scoped_incident(db, principal, incident_id)
    return _detail(db, incident)


@router.post("/{incident_id}/acknowledge", response_model=IncidentDetailResponse)
def acknowledge_incident_endpoint(
    incident_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> IncidentDetailResponse:
    principal = _require_owner(request, db)
    incident = get_scoped_incident(db, principal, incident_id)
    incident = acknowledge_incident(db, principal, incident)
    return _detail(db, incident)


@router.post("/{incident_id}/resolve", response_model=IncidentDetailResponse)
def resolve_incident_endpoint(
    incident_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> IncidentDetailResponse:
    principal = _require_owner(request, db)
    incident = get_scoped_incident(db, principal, incident_id)
    incident = resolve_incident(db, principal, incident)
    return _detail(db, incident)
