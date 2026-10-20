"""PolicyDecision model — final enforcement outcome for one action."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class PolicyDecision(Base):
    __tablename__ = "policy_decisions"
    __table_args__ = (
        Index("ix_policy_decisions_organization_decided_at", "organization_id", "decided_at"),
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
    # Outcomes: ALLOW | REQUIRES_APPROVAL | BLOCK | BLOCKED_FAIL_CLOSED
    outcome: Mapped[str] = mapped_column(String(50), nullable=False)
    policy_reason: Mapped[str] = mapped_column(Text, nullable=False)
    # Human-readable plain-language explanation
    plain_reason: Mapped[str] = mapped_column(Text, nullable=False)
    # Severity levels: LOW | MEDIUM | HIGH | CRITICAL
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="LOW")
    triggered_quarantine: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Whether the mock tool was actually executed after this decision
    tool_executed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tool_result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)

    # Relationships
    action_request: Mapped["ActionRequest"] = relationship(back_populates="policy_decision")
    organization: Mapped["Organization"] = relationship()

    def __repr__(self) -> str:
        return f"<PolicyDecision id={self.id!r} outcome={self.outcome!r}>"
