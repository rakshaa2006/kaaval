"""Organization model."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = (Index("ix_organizations_created_at", "created_at"),)

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # One of: SYNTHETIC_DEMO | STAGING
    environment: Mapped[str] = mapped_column(String(50), nullable=False, default="SYNTHETIC_DEMO")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )

    # Relationships
    users: Mapped[list["User"]] = relationship(back_populates="organization")
    auth_sessions: Mapped[list["AuthSession"]] = relationship(back_populates="organization")
    tasks: Mapped[list["Task"]] = relationship(back_populates="organization")
    source_documents: Mapped[list["SourceDocument"]] = relationship(back_populates="organization")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="organization")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="organization")
    audit_events: Mapped[list["AuditEvent"]] = relationship(back_populates="organization")
    attack_runs: Mapped[list["AttackRun"]] = relationship(back_populates="organization")
    attack_cases: Mapped[list["AttackCase"]] = relationship(back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization id={self.id!r} name={self.name!r}>"
