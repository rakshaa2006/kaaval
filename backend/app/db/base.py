"""SQLAlchemy engine and session factory for Kaaval.

Uses SQLite for local development and can be switched to PostgreSQL for staging
by changing the DATABASE_URL environment variable.
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine, event, inspect, text
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
    upgrade_sqlite_schema(engine)


def upgrade_sqlite_schema(database_engine=engine) -> None:
    """Apply safe additive SQLite changes needed by the current seed schema."""
    if database_engine.dialect.name != "sqlite":
        return

    with database_engine.begin() as connection:
        user_columns = {
            column["name"] for column in inspect(connection).get_columns("users")
        }
        if "status" not in user_columns:
            connection.execute(
                text(
                    "ALTER TABLE users ADD COLUMN status "
                    "VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'"
                )
            )

        if inspect(connection).has_table("auth_sessions"):
            session_columns = {
                column["name"]
                for column in inspect(connection).get_columns("auth_sessions")
            }
            if "organization_id" not in session_columns:
                connection.execute(
                    text(
                        "ALTER TABLE auth_sessions ADD COLUMN organization_id "
                        "VARCHAR(36) REFERENCES organizations(id)"
                    )
                )
                if "organization_id" in user_columns:
                    connection.execute(
                        text(
                            "UPDATE auth_sessions SET organization_id = "
                            "(SELECT organization_id FROM users "
                            "WHERE users.id = auth_sessions.user_id) "
                            "WHERE organization_id IS NULL"
                        )
                    )
                if "created_at" in session_columns:
                    connection.execute(
                        text(
                            "CREATE INDEX IF NOT EXISTS "
                            "ix_auth_sessions_organization_created_at "
                            "ON auth_sessions (organization_id, created_at)"
                        )
                    )

        if inspect(connection).has_table("task_passports"):
            passport_columns = {
                column["name"]
                for column in inspect(connection).get_columns("task_passports")
            }
            if "generation_metadata_json" not in passport_columns:
                connection.execute(
                    text(
                        "ALTER TABLE task_passports ADD COLUMN "
                        "generation_metadata_json TEXT"
                    )
                )

        if inspect(connection).has_table("attack_runs"):
            attack_run_columns = {
                column["name"]
                for column in inspect(connection).get_columns("attack_runs")
            }
            if "updated_at" not in attack_run_columns:
                connection.execute(
                    text(
                        "ALTER TABLE attack_runs ADD COLUMN updated_at DATETIME "
                        "NOT NULL DEFAULT '1970-01-01 00:00:00'"
                    )
                )
                if "created_at" in attack_run_columns:
                    connection.execute(
                        text("UPDATE attack_runs SET updated_at = created_at")
                    )


def get_db():
    """FastAPI dependency: yield a database session, close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
