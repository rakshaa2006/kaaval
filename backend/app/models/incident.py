"""Incident model — containment record for a severe unsafe session event."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        Index("ix_incidents_organization_created_at", "organization_id", "created_at"),
        Index("ix_incidents_session_created_at", "agent_session_id", "created_at"),
        Index("ix_incidents_owner_review_status", "owner_review_status"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agent_sessions.id"), nullable=False, index=True
    )
    # The action_request that triggered the incident
    triggering_action_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("action_requests.id"), nullable=True
    )
    # Severity: LOW | MEDIUM | HIGH | CRITICAL
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="HIGH")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    # Containment status: PENDING | CONTAINED | FAILED
    containment_status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    # Owner review: OPEN | REVIEWED | RESOLVED
    owner_review_status: Mapped[str] = mapped_column(String(50), nullable=False, default="OPEN")
    # Recovery: NOT_STARTED | RESTRICTED_RESTART_CREATED | NOT_AVAILABLE
    recovery_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="NOT_STARTED"
    )
    # ID of the new restricted agent session created via safe restart
    restart_session_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("agent_sessions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="incidents")
    agent_session: Mapped["AgentSession"] = relationship(
        back_populates="incidents", foreign_keys=[agent_session_id]
    )
    organization: Mapped["Organization"] = relationship(back_populates="incidents")
    restart_session: Mapped[Optional["AgentSession"]] = relationship(
        foreign_keys=[restart_session_id]
    )
    notifications: Mapped[list["Notification"]] = relationship(back_populates="incident")

    def __repr__(self) -> str:
        return (
            f"<Incident id={self.id!r} severity={self.severity!r} "
            f"containment={self.containment_status!r}>"
        )
