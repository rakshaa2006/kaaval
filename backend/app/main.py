"""Kaaval FastAPI application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.auth import router as auth_router
from app.api.actions import router as actions_router
from app.api.errors import (
    APIError,
    api_error_handler,
    request_validation_error_handler,
)
from app.api.health import router as health_router
from app.api.tasks import router as tasks_router
from app.db.base import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize the local database on startup."""
    create_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Kaaval",
        description="Minimal backend skeleton for local synthetic development.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)

    app.include_router(health_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    app.include_router(tasks_router, prefix="/api")
    app.include_router(actions_router, prefix="/api")

    return app


app = create_app()
