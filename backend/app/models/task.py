"""Task model."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

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
    # Task states: PASSPORT_GENERATING | PASSPORT_GENERATION_FAILED | PASSPORT_REVIEW
    #              | ACTIVE | RUNNING | COMPLETED | EXPIRED | CANCELLED
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PASSPORT_GENERATING")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="tasks")
    passports: Mapped[list["TaskPassport"]] = relationship(back_populates="task")
    agent_sessions: Mapped[list["AgentSession"]] = relationship(back_populates="task")
    action_requests: Mapped[list["ActionRequest"]] = relationship(back_populates="task")

    def __repr__(self) -> str:
        return f"<Task id={self.id!r} status={self.status!r}>"
