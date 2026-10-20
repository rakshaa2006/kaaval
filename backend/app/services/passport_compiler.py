"""Deterministic, local-only compiler for the invoice-summary MVP."""
from __future__ import annotations

import json
from datetime import timedelta

from app.config import get_settings
from app.db.base import utc_now
from app.models import Task, TaskPassport

ALLOWED_TOOLS = ("read_invoice",)
APPROVAL_REQUIRED_TOOLS: tuple[str, ...] = ()
FORBIDDEN_TOOLS = ("send_email", "delete_backup")
DATA_POLICY = {
    "synthetic_data_only": True,
    "allowed_data_sources": ["synthetic_invoice_fixtures"],
    "source_document_instructions": (
        "UNTRUSTED; document instructions cannot expand Passport permissions"
    ),
    "external_transmission": "FORBIDDEN",
    "destructive_operations": "FORBIDDEN",
}


def compile_invoice_passport(task: Task, version: int) -> TaskPassport:
    """Create a fixed-permission Passport; task/document text cannot add tools."""
    if "invoice" not in task.purpose.casefold():
        raise ValueError("The deterministic MVP compiler supports invoice tasks only.")

    return TaskPassport(
        task_id=task.id,
        organization_id=task.organization_id,
        version=version,
        passport_type="STANDARD",
        generation_status="GENERATED",
        activation_status="DRAFT",
        allowed_tools_json=json.dumps(ALLOWED_TOOLS),
        forbidden_tools_json=json.dumps(FORBIDDEN_TOOLS),
        approval_rules_json=json.dumps(APPROVAL_REQUIRED_TOOLS),
        data_constraints_json=json.dumps(DATA_POLICY, sort_keys=True),
        generation_metadata_json=json.dumps(
            {"compiler": "deterministic-invoice-mvp", "external_llm": False},
            sort_keys=True,
        ),
        purpose=task.purpose,
        expires_at=utc_now() + timedelta(hours=get_settings().passport_expire_hours),
    )


def passport_permissions_are_valid(passport: TaskPassport) -> bool:
    """Fail closed if persisted Passport permissions differ from the MVP policy."""
    try:
        allowed_tools = json.loads(passport.allowed_tools_json)
        approval_tools = json.loads(passport.approval_rules_json)
        forbidden_tools = json.loads(passport.forbidden_tools_json)
        data_policy = json.loads(passport.data_constraints_json)
    except (json.JSONDecodeError, TypeError):
        return False
    return (
        allowed_tools == list(ALLOWED_TOOLS)
        and approval_tools == list(APPROVAL_REQUIRED_TOOLS)
        and forbidden_tools == list(FORBIDDEN_TOOLS)
        and data_policy == DATA_POLICY
    )
