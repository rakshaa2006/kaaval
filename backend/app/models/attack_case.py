"""AttackCase model — synthetic case result within an Attack Lab run."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class AttackCase(Base):
    __tablename__ = "attack_cases"
    __table_args__ = (
        UniqueConstraint("attack_run_id", "case_key", name="uq_attack_cases_run_key"),
        Index("ix_attack_cases_organization_created_at", "organization_id", "created_at"),
        Index("ix_attack_cases_run_created_at", "attack_run_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    attack_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("attack_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_key: Mapped[str] = mapped_column(String(100), nullable=False)
    # Case states: PENDING | RUNNING | COMPLETED | FAILED
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    expected_outcome: Mapped[str] = mapped_column(String(50), nullable=False)
    baseline_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    protected_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decision: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    side_effect_occurred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_simulation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )

    organization: Mapped["Organization"] = relationship(back_populates="attack_cases")
    attack_run: Mapped["AttackRun"] = relationship(back_populates="cases")
