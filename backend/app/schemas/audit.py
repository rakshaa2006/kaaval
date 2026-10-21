"""Pydantic schema for organization-scoped audit timeline responses."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    actor_type: str
    actor_id: str | None
    task_id: str | None
    session_id: str | None
    action_id: str | None
    incident_id: str | None
    description: str
    occurred_at: datetime
    sequence: int | None
    is_simulation: bool
