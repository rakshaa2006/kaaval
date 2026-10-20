"""Pydantic schemas for authentication endpoints."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=1024)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class AuthenticatedUserResponse(BaseModel):
    id: str
    organization_id: str
    organization_name: str
    email: str
    role: str
    status: str


class AuthResponse(BaseModel):
    user: AuthenticatedUserResponse
    expires_at: datetime


class LogoutResponse(BaseModel):
    status: str = "logged_out"
