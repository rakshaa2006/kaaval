"""ApprovalRequest model — single-use, time-limited owner approval for one action."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    __table_args__ = (
        Index("ix_approval_requests_organization_created_at", "organization_id", "created_at"),
        Index("ix_approval_requests_status_expires_at", "status", "expires_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    action_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("action_requests.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    # Approval states: PENDING | APPROVED | DENIED | EXPIRED | FAILED
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    # SHA-256 hash of (tool + masked_args + destination) for replay protection
    action_binding_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    masked_content_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    policy_reason: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolved_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)

    # Relationships
    action_request: Mapped["ActionRequest"] = relationship(back_populates="approval_request")
    organization: Mapped["Organization"] = relationship()
    owner: Mapped["User"] = relationship(
        back_populates="approval_requests", foreign_keys=[owner_id]
    )
    resolved_by: Mapped[Optional["User"]] = relationship(
        back_populates="resolved_approval_requests", foreign_keys=[resolved_by_id]
    )

    @property
    def is_pending_and_valid(self) -> bool:
        return self.status == "PENDING" and utc_now() < self.expires_at

    def __repr__(self) -> str:
        return f"<ApprovalRequest id={self.id!r} status={self.status!r}>"
