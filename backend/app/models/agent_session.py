"""AgentSession model — one execution of a task using one active Passport."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AgentSession(Base):
    __tablename__ = "agent_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    passport_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("task_passports.id"), nullable=False, index=True
    )
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    # Optional parent session for safe-restart tracing
    parent_session_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("agent_sessions.id"), nullable=True
    )
    # Session states: STARTING | ACTIVE | WAITING_APPROVAL | COMPLETED | FAILED | EXPIRED | QUARANTINED
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="STARTING")
    quarantine_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quarantined_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="agent_sessions")
    passport: Mapped["TaskPassport"] = relationship(back_populates="agent_sessions")
    action_requests: Mapped[list["ActionRequest"]] = relationship(back_populates="agent_session")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="agent_session")

    def __repr__(self) -> str:
        return f"<AgentSession id={self.id!r} status={self.status!r}>"
