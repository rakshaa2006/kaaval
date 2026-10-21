"""Pydantic schemas for masked privacy-inspection findings."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

FindingType = Literal[
    "PROMPT_INJECTION",
    "CUSTOMER_EMAIL",
    "PHONE_NUMBER",
    "GOVERNMENT_ID_LIKE",
    "CUSTOMER_LIST",
    "EXTERNAL_DATA_EXPOSURE",
    "DESTRUCTIVE_ACTION_REQUEST",
]


class PrivacyFindingResponse(BaseModel):
    category: FindingType
    masked_value: str
    location_hint: str | None
    confidence: float | None


class NotificationResponse(BaseModel):
    id: str
    notification_type: str
    channel: str
    status: str
    created_at: datetime


class IncidentSummaryResponse(BaseModel):
    id: str
    organization_id: str
    agent_session_id: str
    task_id: str
    triggering_action_id: str | None
    severity: str
    summary: str
    containment_status: str
    owner_review_status: str
    recovery_status: str
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class IncidentDetailResponse(IncidentSummaryResponse):
    findings: list[PrivacyFindingResponse]
    notifications: list[NotificationResponse]
