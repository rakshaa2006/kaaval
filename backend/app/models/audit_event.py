"""AuditEvent model — append-only chronological record of system activity."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        UniqueConstraint("organization_id", "sequence", name="uq_audit_events_org_sequence"),
        Index("ix_audit_events_organization_occurred_at", "organization_id", "occurred_at"),
        Index("ix_audit_events_organization_task", "organization_id", "task_id"),
        Index("ix_audit_events_organization_session", "organization_id", "session_id"),
        Index("ix_audit_events_organization_incident", "organization_id", "incident_id"),
    )

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
    # Actor types: OWNER | SYSTEM | AGENT
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    # Related entity IDs (nullable — not all events have all references)
    task_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("agent_sessions.id", ondelete="SET NULL"), nullable=True
    )
    action_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("action_requests.id", ondelete="SET NULL"), nullable=True
    )
    incident_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True
    )
    approval_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True
    )
    # Plain-language description (no raw sensitive values)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # Masked metadata JSON (safe for display)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Whether this event originated from Attack Lab simulation
    is_simulation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Monotonically increasing within an organization for deterministic ordering
    sequence: Mapped[Optional[int]] = mapped_column(nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, index=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="audit_events")
    task: Mapped[Optional["Task"]] = relationship()
    session: Mapped[Optional["AgentSession"]] = relationship()
    action_request: Mapped[Optional["ActionRequest"]] = relationship()
    incident: Mapped[Optional["Incident"]] = relationship()
    approval_request: Mapped[Optional["ApprovalRequest"]] = relationship()

    def __repr__(self) -> str:
        return (
            f"<AuditEvent id={self.id!r} type={self.event_type!r} "
            f"is_simulation={self.is_simulation!r}>"
        )
