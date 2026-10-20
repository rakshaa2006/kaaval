"""Pydantic schemas for task and Task Passport lifecycle endpoints."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    purpose: str = Field(min_length=1, max_length=4000)

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Task purpose cannot be blank.")
        return normalized


class TaskResponse(BaseModel):
    id: str
    organization_id: str
    owner_id: str
    purpose: str
    status: str
    created_at: datetime
    updated_at: datetime


class PassportDataPolicy(BaseModel):
    synthetic_data_only: bool
    allowed_data_sources: list[str]
    source_document_instructions: str
    external_transmission: str
    destructive_operations: str


class PassportResponse(BaseModel):
    id: str
    task_id: str
    organization_id: str
    version: int
    passport_type: str
    generation_status: str
    activation_status: str
    purpose: str
    allowed_tools: list[str]
    approval_required_tools: list[str]
    forbidden_tools: list[str]
    data_policy: PassportDataPolicy
    expires_at: datetime
    activated_at: datetime | None
    created_at: datetime
