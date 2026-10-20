"""AuditEvent model — append-only chronological record of system activity."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Event types match the constants from the architecture doc, e.g.:
    # LOGIN | LOGOUT | TASK_CREATED | PASSPORT_GENERATED | PASSPORT_ACTIVATED |
    # SESSION_CREATED | ACTION_RECEIVED | ACTION_EVALUATING | FINDING_CREATED |
    # ACTION_ALLOWED | ACTION_BLOCKED | ACTION_APPROVAL_REQUIRED | TOOL_EXECUTED |
    # APPROVAL_CREATED | APPROVAL_RESOLVED | SESSION_QUARANTINED | INCIDENT_CREATED |
    # NOTIFICATION_SENT | NOTIFICATION_FAILED | SAFE_RESTART_CREATED |
    # ATTACK_LAB_RUN | DEMO_RESET
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Actor types: OWNER | SYSTEM | AGENT | TELEGRAM_CALLBACK
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    # Related entity IDs (nullable — not all events have all references)
    task_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    action_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    approval_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    # Plain-language description (no raw sensitive values)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # Masked metadata JSON (safe for display)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Whether this event originated from Attack Lab simulation
    is_simulation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Monotonically increasing within an organization for deterministic ordering
    sequence: Mapped[Optional[int]] = mapped_column(nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="audit_events")

    def __repr__(self) -> str:
        return (
            f"<AuditEvent id={self.id!r} type={self.event_type!r} "
            f"is_simulation={self.is_simulation!r}>"
        )
