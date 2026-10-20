"""AuthSession model — browser session tokens (hashed, never plaintext)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        Index("ix_auth_sessions_organization_created_at", "organization_id", "created_at"),
        Index("ix_auth_sessions_user_expires_at", "user_id", "expires_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # SHA-256 hash of the opaque bearer token — never store the raw token
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="auth_sessions")
    organization: Mapped["Organization"] = relationship(back_populates="auth_sessions")

    @property
    def is_active(self) -> bool:
        now = utc_now()
        return self.revoked_at is None and self.expires_at > now

    def __repr__(self) -> str:
        return f"<AuthSession id={self.id!r} user_id={self.user_id!r}>"
