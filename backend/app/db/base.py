"""SQLAlchemy engine and session factory for Kaaval.

Uses SQLite for local development and can be switched to PostgreSQL for staging
by changing the DATABASE_URL environment variable.
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


def utc_now() -> datetime:
    """Return a naive UTC timestamp compatible with SQLite DateTime columns."""
    return datetime.now(UTC).replace(tzinfo=None)


def _get_engine():
    settings = get_settings()
    url = settings.database_url

    connect_args = {}
    if url.startswith("sqlite"):
        # Required for SQLite when used with multi-threaded frameworks
        connect_args = {"check_same_thread": False}

    engine = create_engine(
        url,
        connect_args=connect_args,
        echo=False,  # Set to True to log SQL statements during debugging
    )

    # Enable foreign-key enforcement for SQLite
    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_conn, connection_record):  # noqa: ANN001
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = _get_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=Session,
)


def create_tables() -> None:
    """Create all tables defined by ORM models (idempotent)."""
    # Import all model modules so SQLAlchemy registers their metadata
    import app.models  # noqa: F401
    import app.audit.service  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yield a database session, close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
