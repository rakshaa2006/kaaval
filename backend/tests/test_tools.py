"""Safety and contract tests for the backend-only mock tool registry."""
from __future__ import annotations

import os
import socket
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.tools import (
    UnknownToolError,
    execute_tool,
    list_tools,
    lookup_tool,
)
from app.tools.schemas import (
    DeleteBackupArguments,
    ReadInvoiceArguments,
    SendEmailArguments,
)


def test_all_known_tools_resolve_and_have_argument_schemas() -> None:
    definitions = {definition.name: definition for definition in list_tools()}

    assert set(definitions) == {"read_invoice", "send_email", "delete_backup"}
    assert lookup_tool("read_invoice") is definitions["read_invoice"]
    assert lookup_tool("send_email") is definitions["send_email"]
    assert lookup_tool("delete_backup") is definitions["delete_backup"]
    assert definitions["read_invoice"].argument_schema is ReadInvoiceArguments
    assert definitions["send_email"].argument_schema is SendEmailArguments
    assert definitions["delete_backup"].argument_schema is DeleteBackupArguments


def test_unknown_tool_is_rejected() -> None:
    with pytest.raises(UnknownToolError):
        lookup_tool("run_shell")

    with pytest.raises(UnknownToolError):
        execute_tool("run_shell", {})


@pytest.mark.parametrize(
    ("fixture_key", "expected_invoice", "expected_trust"),
    [
        ("supplier-invoice-clean", "SYN-INV-0042", "TRUSTED"),
        ("supplier-invoice-poisoned", "SYN-INV-0043", "UNTRUSTED"),
    ],
)
def test_read_invoice_reads_only_requested_synthetic_fixture(
    fixture_key: str, expected_invoice: str, expected_trust: str
) -> None:
    result = execute_tool("read_invoice", {"fixture_key": fixture_key})

    assert result.simulated is True
    assert result.output["fixture_key"] == fixture_key
    assert result.output["trust_level"] == expected_trust
    invoice = result.output["invoice"]
    assert isinstance(invoice, dict)
    assert invoice["invoice_number"] == expected_invoice
    assert invoice["supplier"]["contact"].endswith(".example.test")
    if fixture_key == "supplier-invoice-poisoned":
        assert "untrusted_instruction" in invoice
        assert result.output["trust_level"] == "UNTRUSTED"


def test_read_invoice_defaults_to_clean_fixture_and_marks_result_simulated() -> None:
    result = execute_tool("read_invoice", {})

    assert result.simulated is True
    assert result.output["fixture_key"] == "supplier-invoice-clean"


def test_send_email_returns_simulated_only_result() -> None:
    result = execute_tool(
        "send_email",
        {
            "destination": "accounts@supplier.example.test",
            "template": "supplier_invoice_reminder",
        },
    )

    assert result.simulated is True
    assert result.output == {
        "status": "simulated_email_attempt_recorded",
        "destination": "accounts@supplier.example.test",
        "template": "supplier_invoice_reminder",
        "email_sent": False,
    }


def test_delete_backup_returns_simulated_only_result() -> None:
    result = execute_tool(
        "delete_backup", {"backup_id": "synthetic-backup-daily-001"}
    )

    assert result.simulated is True
    assert result.output == {
        "status": "simulated_deletion_attempt_recorded",
        "backup_id": "synthetic-backup-daily-001",
        "deleted": False,
    }


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("read_invoice", {"fixture_key": "..\\..\\secrets.json"}),
        ("read_invoice", {"fixture_key": "supplier-invoice-clean", "path": "x"}),
        ("send_email", {"destination": "real@example.com", "template": "supplier_invoice_reminder"}),
        ("send_email", {"destination": "a@example.test", "template": "freeform"}),
        ("send_email", {"destination": "a@example.test", "template": "supplier_invoice_reminder", "body": "x"}),
        ("delete_backup", {"backup_id": "..\\important.txt"}),
        ("delete_backup", {"backup_id": "synthetic-backup-001", "path": "x"}),
    ],
)
def test_malformed_arguments_are_rejected(
    tool_name: str, arguments: dict[str, object]
) -> None:
    with pytest.raises(ValidationError):
        execute_tool(tool_name, arguments)


def test_mock_execution_makes_no_network_request(monkeypatch) -> None:
    def reject_network(*args, **kwargs):
        _ = args, kwargs
        raise AssertionError("Mock tools must never make network requests.")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(socket.socket, "connect", reject_network)

    email = execute_tool(
        "send_email",
        {
            "destination": "accounts@supplier.example.test",
            "template": "supplier_invoice_reminder",
        },
    )
    deletion = execute_tool(
        "delete_backup", {"backup_id": "synthetic-backup-daily-001"}
    )
    invoice = execute_tool(
        "read_invoice", {"fixture_key": "supplier-invoice-clean"}
    )

    assert email.simulated is True
    assert deletion.simulated is True
    assert invoice.simulated is True


def test_delete_backup_never_deletes_file_or_backup(monkeypatch, tmp_path: Path) -> None:
    backup = tmp_path / "synthetic-backup-daily-001"
    backup.write_text("synthetic backup", encoding="utf-8")

    def reject_delete(*args, **kwargs):
        _ = args, kwargs
        raise AssertionError("Mock tools must never delete files.")

    monkeypatch.setattr(Path, "unlink", reject_delete)
    monkeypatch.setattr(os, "remove", reject_delete)
    monkeypatch.setattr(os, "unlink", reject_delete)

    result = execute_tool(
        "delete_backup", {"backup_id": "synthetic-backup-daily-001"}
    )

    assert result.simulated is True
    assert result.output["deleted"] is False
    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == "synthetic backup"


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("read_invoice", {"fixture_key": "supplier-invoice-clean"}),
        (
            "send_email",
            {
                "destination": "accounts@supplier.example.test",
                "template": "supplier_invoice_reminder",
            },
        ),
        ("delete_backup", {"backup_id": "synthetic-backup-daily-001"}),
    ],
)
def test_every_tool_result_has_simulated_true(
    tool_name: str, arguments: dict[str, object]
) -> None:
    assert execute_tool(tool_name, arguments).simulated is True


def test_tool_metadata_has_expected_side_effect_classification() -> None:
    metadata = {definition.name: definition for definition in list_tools()}

    assert metadata["read_invoice"].category == "read"
    assert metadata["read_invoice"].side_effect == "none"
    assert metadata["send_email"].category == "external_communication"
    assert metadata["send_email"].side_effect == "simulated_only"
    assert metadata["delete_backup"].category == "destructive"
    assert metadata["delete_backup"].side_effect == "simulated_only"


def test_tool_registry_is_not_exposed_as_public_api(client) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert not any("/tools" in path for path in paths)
