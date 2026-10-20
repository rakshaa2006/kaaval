"""Notification model — Telegram/mock delivery intent and result."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_organization_created_at", "organization_id", "created_at"),
        Index("ix_notifications_incident_created_at", "incident_id", "created_at"),
        Index("ix_notifications_status_created_at", "status", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    incident_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("incidents.id"), nullable=True, index=True
    )
    approval_request_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("approval_requests.id"), nullable=True
    )
    # Notification types: EMERGENCY_ALERT | APPROVAL_REQUEST | RETRY_RESULT
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Channel: MOCK (external delivery adapters are not implemented in this step)
    channel: Mapped[str] = mapped_column(String(50), nullable=False, default="MOCK")
    # States: PENDING | SENT | FAILED | RETRYING
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="notifications")
    incident: Mapped[Optional["Incident"]] = relationship(back_populates="notifications")
    approval_request: Mapped[Optional["ApprovalRequest"]] = relationship()

    def __repr__(self) -> str:
        return (
            f"<Notification id={self.id!r} type={self.notification_type!r} "
            f"status={self.status!r}>"
        )
