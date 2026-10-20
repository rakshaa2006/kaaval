"""TaskPassport model — versioned, immutable permission set for one task."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class TaskPassport(Base):
    __tablename__ = "task_passports"
    __table_args__ = (
        CheckConstraint(
            "activation_status IN ('DRAFT', 'ACTIVE', 'SUPERSEDED', 'EXPIRED', 'CANCELLED')",
            name="ck_task_passports_activation_status",
        ),
        UniqueConstraint("task_id", "version", name="uq_task_passports_task_version"),
        Index("ix_task_passports_organization_created_at", "organization_id", "created_at"),
        Index("ix_task_passports_task_activation", "task_id", "activation_status"),
    )

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
    generation_metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="passports")
    organization: Mapped["Organization"] = relationship()
    agent_sessions: Mapped[list["AgentSession"]] = relationship(back_populates="passport")

    @property
    def is_active_and_valid(self) -> bool:
        return (
            self.activation_status == "ACTIVE"
            and self.expires_at is not None
            and utc_now() < self.expires_at
        )

    def __repr__(self) -> str:
        return (
            f"<TaskPassport id={self.id!r} version={self.version!r} "
            f"type={self.passport_type!r} activation={self.activation_status!r}>"
        )
