"""TaskPassport model — versioned, immutable permission set for one task."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TaskPassport(Base):
    __tablename__ = "task_passports"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # Passport types: STANDARD | RESTRICTED_RESTART
    passport_type: Mapped[str] = mapped_column(String(50), nullable=False, default="STANDARD")
    # Generation states: GENERATED | FAILED | INVALID
    generation_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="GENERATED"
    )
    # Activation states: DRAFT | ACTIVE | SUPERSEDED | EXPIRED | CANCELLED
    activation_status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    # JSON-encoded rule sets (stored as text; validated at read time)
    allowed_tools_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    forbidden_tools_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    approval_rules_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    data_constraints_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    # Optional model/provider metadata from LLM generation
    model_metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="passports")
    agent_sessions: Mapped[list["AgentSession"]] = relationship(back_populates="passport")

    @property
    def is_active_and_valid(self) -> bool:
        if self.activation_status != "ACTIVE":
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def __repr__(self) -> str:
        return (
            f"<TaskPassport id={self.id!r} version={self.version!r} "
            f"type={self.passport_type!r} activation={self.activation_status!r}>"
        )
