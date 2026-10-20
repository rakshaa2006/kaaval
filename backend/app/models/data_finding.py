"""DataFinding model — masked sensitive-data detection result."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DataFinding(Base):
    __tablename__ = "data_findings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    action_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("action_requests.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Finding categories: CUSTOMER_EMAIL | PHONE_NUMBER | GOVERNMENT_ID_LIKE
    #                     | CUSTOMER_LIST | PROMPT_INJECTION
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # Masked representation only: e.g. "r***@example.test", "XXXXXX1234"
    masked_value: Mapped[str] = mapped_column(String(500), nullable=False)
    location_hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Confidence score 0.0–1.0
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # Detector that produced this finding, e.g. "regex", "classifier"
    detector: Mapped[str] = mapped_column(String(100), nullable=False, default="regex")
    # Recommended policy action signal (not the final decision)
    recommended_action: Mapped[str] = mapped_column(String(50), nullable=False, default="REVIEW")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    action_request: Mapped["ActionRequest"] = relationship(back_populates="data_findings")

    def __repr__(self) -> str:
        return (
            f"<DataFinding id={self.id!r} category={self.category!r} "
            f"masked={self.masked_value!r}>"
        )
