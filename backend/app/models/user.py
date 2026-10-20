"""User model."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_organization_created_at", "organization_id", "created_at"),)

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    # bcrypt hash — never store plaintext
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    # V1 only role: OWNER_ADMIN
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="OWNER_ADMIN")
    # User states: ACTIVE | DISABLED
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="users")
    auth_sessions: Mapped[list["AuthSession"]] = relationship(back_populates="user")
    tasks: Mapped[list["Task"]] = relationship(back_populates="owner")
    agent_sessions: Mapped[list["AgentSession"]] = relationship(back_populates="owner")
    approval_requests: Mapped[list["ApprovalRequest"]] = relationship(
        back_populates="owner", foreign_keys="ApprovalRequest.owner_id"
    )
    resolved_approval_requests: Mapped[list["ApprovalRequest"]] = relationship(
        back_populates="resolved_by", foreign_keys="ApprovalRequest.resolved_by_id"
    )
    attack_runs: Mapped[list["AttackRun"]] = relationship(back_populates="initiated_by")

    def __repr__(self) -> str:
        return f"<User id={self.id!r} email={self.email!r} role={self.role!r}>"
