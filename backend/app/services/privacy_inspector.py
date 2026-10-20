"""Deterministic privacy and unsafe-context inspection for synthetic actions."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

FindingType = Literal[
    "PROMPT_INJECTION",
    "CUSTOMER_EMAIL",
    "PHONE_NUMBER",
    "GOVERNMENT_ID_LIKE",
    "CUSTOMER_LIST",
    "EXTERNAL_DATA_EXPOSURE",
    "DESTRUCTIVE_ACTION_REQUEST",
]

_EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+\b"
)
_PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\s().-]*){10,15}(?!\d)")
_GOVERNMENT_ID_PATTERN = re.compile(r"(?<!\d)(?:\d[\s-]?){11}\d(?!\d)")
_INJECTION_PATTERN = re.compile(
    r"\b(ignore|override|bypass)\b.{0,80}\b(passport|policy|instructions?)\b",
    re.IGNORECASE,
)
_EXTERNAL_PATTERN = re.compile(
    r"\b(send|forward|transmit|email|share)\b.{0,100}\b(external|outside|organization|invoice|data)\b",
    re.IGNORECASE,
)
_DESTRUCTIVE_PATTERN = re.compile(
    r"\b(delete|remove|destroy|erase)\b.{0,60}\b(backup|file|record|data)\b",
    re.IGNORECASE,
)
_CUSTOMER_LIST_KEYWORDS = ("customer_list", "customers", "client_list")


@dataclass(frozen=True)
class PrivacyFinding:
    category: FindingType
    masked_value: str
    location_hint: str
    confidence: float


@dataclass(frozen=True)
class PrivacyInspection:
    findings: tuple[PrivacyFinding, ...]
    safety_context_valid: bool
    severe_unsafe_action: bool


def _mask_email(value: str) -> str:
    local_part, _, domain = value.partition("@")
    return f"{local_part[:1]}***@{domain}"


def _iter_values(value: object, key: str = "arguments"):
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            yield from _iter_values(child_value, f"{key}.{child_key}")
    elif isinstance(value, (list, tuple)):
        yield key, value
        for index, item in enumerate(value):
            yield from _iter_values(item, f"{key}[{index}]")
    else:
        yield key, value


def inspect_action_context(
    *,
    task_purpose: str | None,
    passport_permissions: tuple[list[str], list[str], list[str]] | None,
    source_trust: str | None,
    source_values: tuple[tuple[str, str], ...] = (),
    tool_name: str,
    arguments: dict[str, object],
    destination: str | None,
    caller_organization_matches: bool,
    caller_authorized: bool,
) -> PrivacyInspection:
    """Inspect supported context and return masked findings only."""
    context_valid = (
        bool(task_purpose and task_purpose.strip())
        and passport_permissions is not None
        and caller_organization_matches
        and caller_authorized
        and source_trust in (None, "TRUSTED", "UNTRUSTED")
    )
    findings: list[PrivacyFinding] = []
    seen: set[tuple[str, str, str]] = set()

    def add(
        category: FindingType,
        masked_value: str,
        location: str,
        confidence: float = 0.95,
    ) -> None:
        marker = (category, masked_value, location)
        if marker not in seen:
            seen.add(marker)
            findings.append(
                PrivacyFinding(category, masked_value, location, confidence)
            )

    values = list(_iter_values(arguments))
    values.append(("task.purpose", task_purpose))
    values.extend(source_values)
    if passport_permissions is not None:
        values.extend(
            (f"passport.permissions.{name}", permission)
            for name, permissions in zip(
                ("allowed", "forbidden", "approval_required"),
                passport_permissions,
            )
            for permission in permissions
        )
    for location, value in values:
        normalized_location = location.casefold()
        if any(keyword in normalized_location for keyword in _CUSTOMER_LIST_KEYWORDS):
            add(
                "CUSTOMER_LIST",
                "Customer list (values masked)",
                location.split("[", 1)[0],
                0.95,
            )
        if isinstance(value, (list, tuple)):
            continue
        if not isinstance(value, str):
            continue
        text = value
        for match in _EMAIL_PATTERN.finditer(text):
            add("CUSTOMER_EMAIL", _mask_email(match.group(0)), location)
        for match in _PHONE_PATTERN.finditer(text):
            if "government_id" in normalized_location:
                continue
            digits = re.sub(r"\D", "", match.group(0))
            add("PHONE_NUMBER", f"***-***-{digits[-4:]}", location)
        for match in _GOVERNMENT_ID_PATTERN.finditer(text):
            digits = re.sub(r"\D", "", match.group(0))
            add("GOVERNMENT_ID_LIKE", f"XXXXXX{digits[-4:]}", location, 0.8)
        if _INJECTION_PATTERN.search(text):
            add("PROMPT_INJECTION", "Instruction override attempt (content masked)", location, 1.0)
        if _EXTERNAL_PATTERN.search(text):
            add("EXTERNAL_DATA_EXPOSURE", "External data transmission request (masked)", location, 1.0)
        if _DESTRUCTIVE_PATTERN.search(text):
            add("DESTRUCTIVE_ACTION_REQUEST", "Destructive request (content masked)", location, 1.0)

    if tool_name == "send_email" or destination is not None:
        masked_destination = (
            _mask_email(destination)
            if destination and _EMAIL_PATTERN.fullmatch(destination)
            else "External destination (masked)"
        )
        add("EXTERNAL_DATA_EXPOSURE", masked_destination, "action.destination", 1.0)
        if destination and _EMAIL_PATTERN.fullmatch(destination):
            add("CUSTOMER_EMAIL", masked_destination, "action.destination", 0.95)

    if tool_name == "delete_backup":
        add(
            "DESTRUCTIVE_ACTION_REQUEST",
            "Backup deletion request (content masked)",
            "action.tool_name",
            1.0,
        )

    categories = {finding.category for finding in findings}
    prompt_injection_present = "PROMPT_INJECTION" in categories
    action_destructive = any(
        finding.category == "DESTRUCTIVE_ACTION_REQUEST"
        and finding.location_hint.startswith("arguments.")
        for finding in findings
    )
    action_external_exposure = any(
        finding.category == "EXTERNAL_DATA_EXPOSURE"
        and finding.location_hint.startswith("arguments.")
        for finding in findings
    )
    action_sensitive_payload = any(
        finding.category in ("CUSTOMER_EMAIL", "PHONE_NUMBER", "GOVERNMENT_ID_LIKE", "CUSTOMER_LIST")
        and finding.location_hint.startswith("arguments.")
        and "destination" not in finding.location_hint
        for finding in findings
    )
    severe = tool_name == "delete_backup" or action_destructive or (
        tool_name == "send_email"
        and action_external_exposure
        and action_sensitive_payload
    ) or (
        "EXTERNAL_DATA_EXPOSURE" in categories
        and prompt_injection_present
        and tool_name == "send_email"
    )
    return PrivacyInspection(tuple(findings), context_valid, severe)
