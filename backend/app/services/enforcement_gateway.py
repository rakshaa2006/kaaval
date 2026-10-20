"""Internal policy gateway for all protected mock-tool execution."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import APIError
from app.audit.service import append_audit_event
from app.auth.service import AuthenticatedUser
from app.db.base import utc_now
from app.models import (
    ActionRequest,
    AgentSession,
    DataFinding,
    PolicyDecision,
    SourceDocument,
    Task,
    TaskPassport,
)
from app.schemas.actions import (
    ActionCreateRequest,
    ActionDecisionResponse,
    ActionFindingResponse,
    ActionResponse,
    DecisionOutcome,
)
from app.tools import (
    ToolRegistryError,
    UnknownToolError,
    execute_tool,
    lookup_tool,
)

_EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+\b"
)
_PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\s().-]*){10,15}(?!\d)")
_CREDENTIAL_PATTERN = re.compile(
    r"(?i)\b(password|token|secret|api[_ ]key)\s*[:=]\s*\S+"
)
_SENSITIVE_KEYS = (
    "password",
    "secret",
    "token",
    "authorization",
    "authoriz",
    "organization_id",
    "user_id",
    "role",
    "phone",
    "body",
    "message",
    "content",
)
_OUTCOME_EVENT = {
    "ALLOW": "ACTION_ALLOWED",
    "REQUIRES_APPROVAL": "ACTION_APPROVAL_REQUIRED",
    "BLOCK": "ACTION_BLOCKED",
    "BLOCKED_FAIL_CLOSED": "ACTION_BLOCKED",
}


@dataclass
class _Evaluation:
    outcome: DecisionOutcome
    reason_code: str
    reason: str
    source_document: SourceDocument | None = None
    validated_arguments: BaseModel | None = None
    findings: list[DataFinding] = field(default_factory=list)


def _mask_email(value: str) -> str:
    local_part, _, domain = value.partition("@")
    return f"{local_part[:1]}***@{domain}"


def _sanitize(value: object, key: str = "") -> object:
    normalized_key = key.casefold()
    if any(marker in normalized_key for marker in _SENSITIVE_KEYS):
        if "@" in str(value):
            return _mask_email(str(value))
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(child_key): _sanitize(child_value, str(child_key))
                for child_key, child_value in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    if isinstance(value, str):
        masked = _EMAIL_PATTERN.sub(lambda match: _mask_email(match.group(0)), value)
        masked = _PHONE_PATTERN.sub("[REDACTED_PHONE]", masked)
        return _CREDENTIAL_PATTERN.sub(r"\1=[REDACTED]", masked)
    return value


def _masked_email_destination(value: str | None) -> str | None:
    if value is None:
        return None
    return _EMAIL_PATTERN.sub(lambda match: _mask_email(match.group(0)), value)


def _permission_lists(passport: TaskPassport) -> tuple[list[str], list[str], list[str]] | None:
    try:
        allowed = json.loads(passport.allowed_tools_json)
        forbidden = json.loads(passport.forbidden_tools_json)
        approval_required = json.loads(passport.approval_rules_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not all(
        isinstance(value, list) and all(isinstance(item, str) for item in value)
        for value in (allowed, forbidden, approval_required)
    ):
        return None
    if (
        len(set(allowed)) != len(allowed)
        or len(set(forbidden)) != len(forbidden)
        or len(set(approval_required)) != len(approval_required)
        or set(allowed) & set(forbidden)
        or set(allowed) & set(approval_required)
        or set(forbidden) & set(approval_required)
    ):
        return None
    return allowed, forbidden, approval_required


def _data_policy_is_valid(passport: TaskPassport) -> bool:
    try:
        constraints = json.loads(passport.data_constraints_json)
    except (json.JSONDecodeError, TypeError):
        return False
    return (
        isinstance(constraints, dict)
        and constraints.get("synthetic_data_only") is True
        and isinstance(constraints.get("allowed_data_sources"), list)
        and "synthetic_invoice_fixtures" in constraints["allowed_data_sources"]
    )


def _find_source_document(
    db: Session,
    organization_id: str,
    request: ActionCreateRequest,
    arguments: BaseModel,
) -> SourceDocument | None:
    fixture_key = getattr(arguments, "fixture_key", None)
    if fixture_key is not None:
        document = db.scalar(
            select(SourceDocument).where(
                SourceDocument.organization_id == organization_id,
                SourceDocument.fixture_key == fixture_key,
                SourceDocument.is_synthetic.is_(True),
            )
        )
        if document is None:
            return None
        if request.source_document_id and str(request.source_document_id) != document.id:
            return None
        return document
    if request.source_document_id is None:
        return None
    return db.scalar(
        select(SourceDocument).where(
            SourceDocument.id == str(request.source_document_id),
            SourceDocument.organization_id == organization_id,
            SourceDocument.is_synthetic.is_(True),
        )
    )


def _evaluate_action(
    db: Session,
    principal: AuthenticatedUser,
    request: ActionCreateRequest,
    session: AgentSession,
    task: Task,
    passport: TaskPassport | None,
) -> _Evaluation:
    if task.organization_id != principal.organization_id or task.owner_id != principal.user.id:
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "TASK_SCOPE_MISMATCH",
            "Task ownership could not be verified.",
        )
    if session.task_id != task.id or session.organization_id != principal.organization_id:
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "SESSION_SCOPE_MISMATCH",
            "Session and task context do not match.",
        )
    if task.status not in ("ACTIVE", "RUNNING"):
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "TASK_NOT_ACTIVE",
            "Task is not active for action execution.",
        )
    if session.status == "QUARANTINED":
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "SESSION_QUARANTINED",
            "Quarantined sessions cannot execute actions.",
        )
    if session.status != "ACTIVE":
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "SESSION_NOT_ACTIVE",
            "Session is not active.",
        )
    if passport is None:
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "PASSPORT_MISSING",
            "An active Task Passport could not be verified.",
        )
    if (
        passport.task_id != task.id
        or passport.organization_id != principal.organization_id
        or passport.id != session.passport_id
    ):
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "PASSPORT_SCOPE_MISMATCH",
            "Task Passport context could not be verified.",
        )
    if passport.activation_status != "ACTIVE":
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "PASSPORT_NOT_ACTIVE",
            "Task Passport is not active.",
        )
    if passport.generation_status != "GENERATED" or not _data_policy_is_valid(passport):
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "PASSPORT_POLICY_INVALID",
            "Task Passport safety constraints could not be verified.",
        )
    if passport.expires_at is None or passport.expires_at <= utc_now():
        if passport.activation_status == "ACTIVE":
            passport.activation_status = "EXPIRED"
        task.status = "EXPIRED"
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "PASSPORT_EXPIRED",
            "Task Passport has expired.",
        )

    try:
        definition = lookup_tool(request.tool_name)
    except UnknownToolError:
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "UNKNOWN_TOOL",
            "Tool is not registered.",
        )

    try:
        arguments = definition.argument_schema.model_validate(request.arguments)
    except ValidationError:
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "INVALID_ARGUMENTS",
            "Tool arguments failed validation.",
        )

    permissions = _permission_lists(passport)
    if permissions is None:
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "INVALID_PASSPORT_PERMISSIONS",
            "Task Passport permissions could not be verified.",
            validated_arguments=arguments,
        )
    allowed, forbidden, approval_required = permissions

    source_document: SourceDocument | None = None
    findings: list[DataFinding] = []
    if request.tool_name == "read_invoice":
        source_document = _find_source_document(
            db, principal.organization_id, request, arguments
        )
        if source_document is None:
            return _Evaluation(
                "BLOCKED_FAIL_CLOSED", "SOURCE_CONTEXT_MISSING",
                "A matching synthetic source document is required.",
                validated_arguments=arguments,
            )
        if source_document.trust_level not in ("TRUSTED", "UNTRUSTED"):
            return _Evaluation(
                "BLOCKED_FAIL_CLOSED", "SOURCE_TRUST_UNAVAILABLE",
                "Source document trust could not be verified.",
                source_document=source_document,
                validated_arguments=arguments,
            )
        if "invoice" not in task.purpose.casefold():
            return _Evaluation(
                "BLOCK", "TASK_PURPOSE_MISMATCH",
                "Invoice reading is outside the task purpose.",
                source_document=source_document,
                validated_arguments=arguments,
            )
        if source_document.trust_level == "UNTRUSTED":
            findings.append(
                DataFinding(
                    organization_id=principal.organization_id,
                    category="PROMPT_INJECTION",
                    masked_value="Untrusted source instruction (content masked)",
                    location_hint="invoice.untrusted_instruction",
                    confidence=1.0,
                    detector="synthetic_fixture_metadata",
                    recommended_action="REVIEW",
                )
            )

    if request.tool_name == "delete_backup":
        return _Evaluation(
            "BLOCK", "DESTRUCTIVE_TOOL_FORBIDDEN",
            "Destructive tools are disabled for this MVP.",
            source_document=source_document,
            validated_arguments=arguments,
            findings=findings,
        )
    if request.tool_name == "send_email":
        return _Evaluation(
            "BLOCK", "EXTERNAL_COMMUNICATION_FORBIDDEN",
            "External communication is disabled for this MVP.",
            source_document=source_document,
            validated_arguments=arguments,
            findings=findings,
        )
    if request.tool_name in forbidden:
        return _Evaluation(
            "BLOCK", "TOOL_FORBIDDEN_BY_PASSPORT",
            "Task Passport forbids this tool.",
            source_document=source_document,
            validated_arguments=arguments,
            findings=findings,
        )
    if request.tool_name in approval_required:
        return _Evaluation(
            "REQUIRES_APPROVAL", "APPROVAL_REQUIRED",
            "Task Passport requires owner approval for this tool.",
            source_document=source_document,
            validated_arguments=arguments,
            findings=findings,
        )
    if request.tool_name not in allowed:
        return _Evaluation(
            "BLOCK", "TOOL_NOT_ALLOWED_BY_PASSPORT",
            "Task Passport does not allow this tool.",
            source_document=source_document,
            validated_arguments=arguments,
            findings=findings,
        )
    if request.tool_name != "read_invoice" or definition.category != "read":
        return _Evaluation(
            "BLOCKED_FAIL_CLOSED", "UNSUPPORTED_MVP_TOOL",
            "Tool is not executable in the current MVP policy.",
            source_document=source_document,
            validated_arguments=arguments,
            findings=findings,
        )
    return _Evaluation(
        "ALLOW", "INVOICE_READ_ALLOWED",
        "Invoice read is allowed by the active Passport.",
        source_document=source_document,
        validated_arguments=arguments,
        findings=findings,
    )


def _audit_action(
    db: Session,
    principal: AuthenticatedUser,
    session: AgentSession,
    action: ActionRequest,
    decision: PolicyDecision,
) -> None:
    append_audit_event(
        db,
        organization_id=principal.organization_id,
        task_id=action.task_id,
        session_id=session.id,
        action_id=action.id,
        actor_type="OWNER",
        actor_id=principal.user.id,
        event_type=_OUTCOME_EVENT[decision.outcome],
        description=f"Action evaluated: {decision.outcome}.",
        metadata_json=json.dumps(
            {
                "outcome": decision.outcome,
                "reason_code": decision.policy_reason,
                "tool_name": action.tool_name,
            },
            sort_keys=True,
        ),
        is_simulation=True,
    )


def _response(
    action: ActionRequest,
    decision: PolicyDecision,
    findings: list[DataFinding],
) -> ActionResponse:
    result = (
        json.loads(decision.tool_result_json)
        if decision.tool_result_json is not None
        else None
    )
    return ActionResponse(
        action_id=action.id,
        request_id=action.request_id,
        tool_name=action.tool_name,
        decision=ActionDecisionResponse(
            outcome=decision.outcome,
            reason_code=decision.policy_reason,
            reason=decision.plain_reason,
            tool_executed=decision.tool_executed,
        ),
        result=result,
        findings=[
            ActionFindingResponse(
                category=finding.category,
                masked_value=finding.masked_value,
                location_hint=finding.location_hint,
            )
            for finding in findings
        ],
        created_at=action.created_at,
    )


def enforce_action(
    db: Session,
    principal: AuthenticatedUser,
    session_id: str,
    request: ActionCreateRequest,
) -> ActionResponse:
    if principal.user.role != "OWNER_ADMIN":
        raise APIError(403, "FORBIDDEN", "Owner permissions are required.")

    agent_session = db.scalar(
        select(AgentSession).where(
            AgentSession.id == session_id,
            AgentSession.organization_id == principal.organization_id,
            AgentSession.owner_id == principal.user.id,
        )
    )
    if agent_session is None:
        raise APIError(404, "SESSION_NOT_FOUND", "Session was not found.")
    task = db.get(Task, agent_session.task_id)
    passport = db.scalar(
        select(TaskPassport).where(
            TaskPassport.id == agent_session.passport_id,
            TaskPassport.organization_id == principal.organization_id,
        )
    )
    evaluation = _evaluate_action(
        db, principal, request, agent_session, task, passport
    )

    validated_arguments = (
        evaluation.validated_arguments.model_dump(mode="json")
        if evaluation.validated_arguments is not None
        else request.arguments
    )
    try:
        lookup_tool(request.tool_name)
        safe_tool_name = request.tool_name
    except UnknownToolError:
        safe_tool_name = "unknown"
    destination = validated_arguments.get("destination")
    action = ActionRequest(
        organization_id=principal.organization_id,
        task_id=agent_session.task_id,
        session_id=agent_session.id,
        request_id=str(request.request_id),
        tool_name=safe_tool_name,
        masked_arguments_json=json.dumps(
            _sanitize(validated_arguments), sort_keys=True
        ),
        destination=_masked_email_destination(
            destination if isinstance(destination, str) else None
        ),
        source_document_id=(
            evaluation.source_document.id
            if evaluation.source_document is not None
            else None
        ),
        source_trust=(
            evaluation.source_document.trust_level
            if evaluation.source_document is not None
            else "UNKNOWN"
        ),
        purpose_context=_sanitize(task.purpose) if task is not None else None,
    )
    db.add(action)
    db.flush()

    decision = PolicyDecision(
        action_request_id=action.id,
        organization_id=principal.organization_id,
        outcome=evaluation.outcome,
        policy_reason=evaluation.reason_code,
        plain_reason=evaluation.reason,
        severity="HIGH" if evaluation.outcome == "BLOCKED_FAIL_CLOSED" else "LOW",
        triggered_quarantine=False,
        tool_executed=False,
    )
    db.add(decision)
    for finding in evaluation.findings:
        finding.action_request_id = action.id
        db.add(finding)
    db.flush()
    db.commit()

    if decision.outcome == "ALLOW":
        try:
            raw_result = execute_tool(
                request.tool_name,
                evaluation.validated_arguments.model_dump(mode="json"),
            )
            safe_result = _sanitize(raw_result.model_dump(mode="json"))
            decision.tool_executed = True
            decision.tool_result_json = json.dumps(safe_result, sort_keys=True)
        except (ToolRegistryError, ValidationError, OSError):
            decision.tool_result_json = json.dumps(
                {"error_code": "MOCK_TOOL_EXECUTION_FAILED"}
            )
            decision.plain_reason = (
                "Policy allowed the action, but the synthetic tool failed safely."
            )
    else:
        decision.tool_result_json = None

    _audit_action(db, principal, agent_session, action, decision)
    db.commit()
    return _response(action, decision, evaluation.findings)
