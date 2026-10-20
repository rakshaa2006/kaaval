"""Common Pydantic schemas shared across the API.

Includes the standard error envelope and health response schemas.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorEnvelope(BaseModel):
    """Standard error response returned by every API error handler."""

    code: str = Field(..., description="Machine-readable error code, e.g. SESSION_QUARANTINED")
    message: str = Field(..., description="Human-readable plain-language explanation")
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = Field(None, description="Request ID for log correlation")


class HealthResponse(BaseModel):
    """Response for GET /api/health."""

    status: str = Field(..., description="'ok' when the application is running")
    env: str = Field(..., description="Current APP_ENV value")
    version: str = Field(..., description="Application version string")


class ReadyResponse(BaseModel):
    """Response for GET /api/ready."""

    status: str = Field(..., description="'ready' when the database is reachable")
    database: str = Field(..., description="Database connectivity state")
