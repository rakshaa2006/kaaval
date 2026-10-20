"""SourceDocument model — seeded synthetic fixture references."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class SourceDocument(Base):
    __tablename__ = "source_documents"
    __table_args__ = (
        UniqueConstraint("organization_id", "fixture_key", name="uq_source_documents_org_fixture"),
        Index("ix_source_documents_organization_created_at", "organization_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Key used to locate the fixture file, e.g. "supplier-invoice-clean"
    fixture_key: Mapped[str] = mapped_column(String(255), nullable=False)
    # SHA-256 hash of the fixture file content
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    # Source trust levels: TRUSTED | UNTRUSTED | UNKNOWN
    trust_level: Mapped[str] = mapped_column(String(50), nullable=False, default="UNTRUSTED")
    is_synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="source_documents")
    action_requests: Mapped[list["ActionRequest"]] = relationship(
        back_populates="source_document"
    )

    def __repr__(self) -> str:
        return f"<SourceDocument id={self.id!r} fixture_key={self.fixture_key!r}>"
