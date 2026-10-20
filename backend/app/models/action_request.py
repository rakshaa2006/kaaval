"""ActionRequest model — one proposed tool call from the agent."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ActionRequest(Base):
    __tablename__ = "action_requests"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id"), nullable=False, index=True
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agent_sessions.id"), nullable=False, index=True
    )
    # Opaque client-assigned request ID for idempotency
    request_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Masked arguments only — never store raw sensitive values
    masked_arguments_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    destination: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    source_document_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("source_documents.id"), nullable=True
    )
    # Source trust: TRUSTED | UNTRUSTED | UNKNOWN
    source_trust: Mapped[str] = mapped_column(String(50), nullable=False, default="UNKNOWN")
    purpose_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="action_requests")
    agent_session: Mapped["AgentSession"] = relationship(back_populates="action_requests")
    source_document: Mapped[Optional["SourceDocument"]] = relationship(
        back_populates="action_requests"
    )
    policy_decision: Mapped[Optional["PolicyDecision"]] = relationship(
        back_populates="action_request", uselist=False
    )
    data_findings: Mapped[list["DataFinding"]] = relationship(back_populates="action_request")
    approval_request: Mapped[Optional["ApprovalRequest"]] = relationship(
        back_populates="action_request", uselist=False
    )

    def __repr__(self) -> str:
        return f"<ActionRequest id={self.id!r} tool={self.tool_name!r}>"
