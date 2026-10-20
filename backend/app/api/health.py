"""Health and readiness endpoints.

GET /api/health  — liveness probe: returns 200 when the application is running.
GET /api/ready   — readiness probe: returns 200 when the database is reachable.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.base import get_db
from app.schemas.common import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health"])

_APP_VERSION = "0.1.0"


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Returns 200 when the application process is running.",
)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        env=settings.app_env.value,
        version=_APP_VERSION,
    )


@router.get(
    "/ready",
    response_model=ReadyResponse,
    summary="Readiness probe",
    description="Returns 200 when the application can reach the database.",
)
def ready(db: Session = Depends(get_db)) -> ReadyResponse:
    try:
        db.execute(text("SELECT 1"))
        return ReadyResponse(status="ready", database="connected")
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "DATABASE_UNAVAILABLE",
                "message": "The application cannot reach the database.",
                "details": {},
                "request_id": None,
            },
        ) from exc
