"""Task model."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PASSPORT_GENERATING', 'PASSPORT_REVIEW', 'ACTIVE', "
            "'RUNNING', 'COMPLETED', 'EXPIRED', 'CANCELLED')",
            name="ck_tasks_status",
        ),
        Index("ix_tasks_organization_created_at", "organization_id", "created_at"),
        Index("ix_tasks_organization_status", "organization_id", "status"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    # Task states: PASSPORT_GENERATING | PASSPORT_REVIEW | ACTIVE | RUNNING
    #              | COMPLETED | EXPIRED | CANCELLED
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PASSPORT_GENERATING")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="tasks")
    owner: Mapped["User"] = relationship(back_populates="tasks")
    passports: Mapped[list["TaskPassport"]] = relationship(back_populates="task")
    agent_sessions: Mapped[list["AgentSession"]] = relationship(back_populates="task")
    action_requests: Mapped[list["ActionRequest"]] = relationship(back_populates="task")

    def __repr__(self) -> str:
        return f"<Task id={self.id!r} status={self.status!r}>"
