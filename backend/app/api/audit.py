"""Organization-scoped audit timeline endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import APIError
from app.auth.service import get_authenticated_user, get_session_token
from app.db.base import get_db
from app.models import AuditEvent
from app.schemas.audit import AuditEventResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditEventResponse])
def list_audit_events(
    request: Request,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[AuditEventResponse]:
    principal = get_authenticated_user(db, get_session_token(request))
    if principal is None:
        raise APIError(401, "UNAUTHENTICATED", "Authentication is required.")

    events = db.scalars(
        select(AuditEvent)
        .where(AuditEvent.organization_id == principal.organization_id)
        .order_by(AuditEvent.sequence.desc())
        .limit(limit)
    ).all()
    return [AuditEventResponse.model_validate(event) for event in events]
