"""Kaaval FastAPI application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.health import router as health_router
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

    app.include_router(health_router, prefix="/api")

    return app


app = create_app()
