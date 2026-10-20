"""AttackRun model — one Attack Lab simulation run and its cases."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class AttackRun(Base):
    """A single Attack Lab simulation run.

    One run may contain multiple cases (stored in attack_cases).
    Results are always labelled SIMULATION and must not appear in live incident feeds.
    """

    __tablename__ = "attack_runs"
    __table_args__ = (
        Index("ix_attack_runs_organization_created_at", "organization_id", "created_at"),
        Index("ix_attack_runs_status_created_at", "status", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    initiated_by_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    # Run statuses: RUNNING | COMPLETED | FAILED | RESET
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="RUNNING")
    # JSON array of case keys that were run
    case_keys_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # JSON summary of baseline vs protected results
    results_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="attack_runs")
    initiated_by: Mapped["User"] = relationship(back_populates="attack_runs")
    cases: Mapped[list["AttackCase"]] = relationship(
        back_populates="attack_run", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AttackRun id={self.id!r} status={self.status!r}>"
