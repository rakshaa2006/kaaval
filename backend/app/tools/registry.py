"""Internal registry and execution service for synthetic mock tools.

This module deliberately has no HTTP routes or external adapters. The future
Enforcement Gateway can call ``execute_tool`` after authorizing a request.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.tools.schemas import (
    DeleteBackupArguments,
    ReadInvoiceArguments,
    SendEmailArguments,
)

ToolCategory = Literal["read", "external_communication", "destructive"]
SideEffect = Literal["none", "simulated_only"]

_FIXTURE_DIRECTORY = Path(__file__).resolve().parents[3] / "fixtures" / "invoices"
_FIXTURE_FILENAMES = {
    "supplier-invoice-clean": "supplier-invoice-clean.json",
    "supplier-invoice-poisoned": "supplier-invoice-poisoned.json",
}


class ToolRegistryError(Exception):
    """Base class for internal tool registry errors."""


class UnknownToolError(ToolRegistryError, KeyError):
    """Raised when a tool name is not registered."""


class SyntheticFixtureError(ToolRegistryError):
    """Raised when an allowlisted fixture is missing or not synthetic."""


class ToolResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str
    simulated: Literal[True] = True
    output: dict[str, object]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    category: ToolCategory
    side_effect: SideEffect
    argument_schema: type[BaseModel]
    _executor: Callable[[BaseModel], dict[str, object]] = field(repr=False)


class _FixtureMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fixture_key: str
    description: str
    is_synthetic: Literal[True]
    trust_level: Literal["TRUSTED", "UNTRUSTED"]


class _InvoiceSupplier(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    contact: str

    @field_validator("contact")
    @classmethod
    def require_synthetic_contact(cls, value: str) -> str:
        if not value.lower().endswith(".example.test"):
            raise ValueError("Synthetic invoice fixture contains a non-synthetic contact.")
        return value


class _Invoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supplier: _InvoiceSupplier
    invoice_number: str
    invoice_date: str
    due_date: str
    amount_inr: int = Field(gt=0)
    currency: Literal["INR"]
    description: str
    untrusted_instruction: str | None = None


class _InvoiceFixture(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: _FixtureMetadata = Field(alias="_meta")
    invoice: _Invoice


def _read_invoice(arguments: BaseModel) -> dict[str, object]:
    validated_arguments = ReadInvoiceArguments.model_validate(arguments)
    fixture_key = validated_arguments.fixture_key
    fixture_path = _FIXTURE_DIRECTORY / _FIXTURE_FILENAMES[fixture_key]
    try:
        content = fixture_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SyntheticFixtureError(
            f"Synthetic invoice fixture {fixture_key!r} could not be read."
        ) from exc
    fixture = _InvoiceFixture.model_validate_json(content)
    if fixture.meta.fixture_key != fixture_key or fixture.meta.is_synthetic is not True:
        raise SyntheticFixtureError(
            f"Invoice fixture {fixture_key!r} failed synthetic fixture validation."
        )
    return {
        "fixture_key": fixture_key,
        "trust_level": fixture.meta.trust_level,
        "invoice": fixture.invoice.model_dump(exclude_none=True),
    }


def _simulate_email(arguments: BaseModel) -> dict[str, object]:
    validated_arguments = SendEmailArguments.model_validate(arguments)
    return {
        "status": "simulated_email_attempt_recorded",
        "destination": validated_arguments.destination,
        "template": validated_arguments.template,
        "email_sent": False,
    }


def _simulate_backup_deletion(arguments: BaseModel) -> dict[str, object]:
    validated_arguments = DeleteBackupArguments.model_validate(arguments)
    return {
        "status": "simulated_deletion_attempt_recorded",
        "backup_id": validated_arguments.backup_id,
        "deleted": False,
    }


_REGISTRY: Mapping[str, ToolDefinition] = MappingProxyType(
    {
        "read_invoice": ToolDefinition(
            name="read_invoice",
            description="Reads an allowlisted synthetic invoice fixture.",
            category="read",
            side_effect="none",
            argument_schema=ReadInvoiceArguments,
            _executor=_read_invoice,
        ),
        "send_email": ToolDefinition(
            name="send_email",
            description="Records a simulated supplier reminder email attempt.",
            category="external_communication",
            side_effect="simulated_only",
            argument_schema=SendEmailArguments,
            _executor=_simulate_email,
        ),
        "delete_backup": ToolDefinition(
            name="delete_backup",
            description="Records a simulated backup deletion attempt.",
            category="destructive",
            side_effect="simulated_only",
            argument_schema=DeleteBackupArguments,
            _executor=_simulate_backup_deletion,
        ),
    }
)


def list_tools() -> tuple[ToolDefinition, ...]:
    """Return metadata for the three registered backend-only tools."""
    return tuple(_REGISTRY.values())


def lookup_tool(name: str) -> ToolDefinition:
    """Resolve one known tool or raise ``UnknownToolError``."""
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        raise UnknownToolError(f"Unknown tool: {name}") from exc


def execute_tool(name: str, arguments: dict[str, object]) -> ToolResult:
    """Validate arguments and execute a registered synthetic tool.

    Email and deletion tools only return an attempt record; neither performs
    network access nor changes files. Execution is internal and has no API route.
    """
    definition = lookup_tool(name)
    validated_arguments = definition.argument_schema.model_validate(arguments)
    output = definition._executor(validated_arguments)
    return ToolResult(tool_name=name, simulated=True, output=output)
