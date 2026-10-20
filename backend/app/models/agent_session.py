"""AgentSession model — one execution of a task using one active Passport."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class AgentSession(Base):
    __tablename__ = "agent_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('STARTING', 'ACTIVE', 'WAITING_APPROVAL', 'COMPLETED', "
            "'FAILED', 'EXPIRED', 'QUARANTINED')",
            name="ck_agent_sessions_status",
        ),
        Index("ix_agent_sessions_organization_created_at", "organization_id", "created_at"),
        Index("ix_agent_sessions_task_created_at", "task_id", "created_at"),
        Index("ix_agent_sessions_status", "status"),
    )

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
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="agent_sessions")
    passport: Mapped["TaskPassport"] = relationship(back_populates="agent_sessions")
    organization: Mapped["Organization"] = relationship()
    owner: Mapped["User"] = relationship(back_populates="agent_sessions")
    parent_session: Mapped[Optional["AgentSession"]] = relationship(
        remote_side="AgentSession.id", back_populates="child_sessions"
    )
    child_sessions: Mapped[list["AgentSession"]] = relationship(back_populates="parent_session")
    action_requests: Mapped[list["ActionRequest"]] = relationship(back_populates="agent_session")
    incidents: Mapped[list["Incident"]] = relationship(
        back_populates="agent_session", foreign_keys="Incident.agent_session_id"
    )

    def __repr__(self) -> str:
        return f"<AgentSession id={self.id!r} status={self.status!r}>"
