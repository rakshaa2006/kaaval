"""Pydantic contracts for action proposals and policy outcomes."""
from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


DecisionOutcome = Literal[
    "ALLOW",
    "REQUIRES_APPROVAL",
    "BLOCK",
    "BLOCKED_FAIL_CLOSED",
]


class ActionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    request_id: UUID = Field(default_factory=uuid4)
    tool_name: str = Field(min_length=1, max_length=100)
    arguments: dict[str, object]
    source_document_id: UUID | None = None


class ActionFindingResponse(BaseModel):
    category: str
    masked_value: str
    location_hint: str | None


class ActionDecisionResponse(BaseModel):
    outcome: DecisionOutcome
    reason_code: str
    reason: str
    tool_executed: bool


class ActionResponse(BaseModel):
    action_id: str
    request_id: str
    tool_name: str
    decision: ActionDecisionResponse
    result: dict[str, object] | None
    findings: list[ActionFindingResponse]
    created_at: datetime
