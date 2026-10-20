"""Authenticated action proposal endpoint routed through the enforcement gateway."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.errors import APIError
from app.auth.service import get_authenticated_user, get_session_token
from app.db.base import get_db
from app.schemas.actions import ActionCreateRequest, ActionResponse
from app.services.enforcement_gateway import enforce_action

router = APIRouter(prefix="/sessions", tags=["actions"])


@router.post("/{session_id}/actions", response_model=ActionResponse)
def create_action(
    session_id: str,
    payload: ActionCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ActionResponse:
    principal = get_authenticated_user(db, get_session_token(request))
    if principal is None:
        raise APIError(401, "UNAUTHENTICATED", "Authentication is required.")
    return enforce_action(db, principal, session_id, payload)
