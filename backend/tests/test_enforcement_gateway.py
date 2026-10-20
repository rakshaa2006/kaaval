"""Integration tests for the authenticated enforcement gateway."""
from __future__ import annotations

import os
import socket
from datetime import timedelta
from pathlib import Path

import pytest
from sqlalchemy import select, update

from app.db.base import utc_now
from app.models import (
    ActionRequest,
    AgentSession,
    AuditEvent,
    DataFinding,
    Incident,
    Notification,
    Organization,
    PolicyDecision,
    SourceDocument,
    TaskPassport,
    User,
)
from app.seed import DEMO_OWNER_EMAIL, DEMO_OWNER_PASSWORD, seed_synthetic_data

FIXTURE_DIRECTORY = Path(__file__).resolve().parents[2] / "fixtures" / "invoices"
INVOICE_PURPOSE = "Summarize supplier invoices and flag overdue ones."


def create_active_session(client, db_session) -> tuple[User, str]:
    seed_synthetic_data(db_session, FIXTURE_DIRECTORY)
    owner = db_session.scalar(select(User).where(User.email == DEMO_OWNER_EMAIL))
    login_result = client.post(
        "/api/auth/login",
        json={"email": DEMO_OWNER_EMAIL, "password": DEMO_OWNER_PASSWORD},
    )
    assert login_result.status_code == 200
    task_result = client.post("/api/tasks", json={"purpose": INVOICE_PURPOSE})
    task_id = task_result.json()["id"]
    passport_result = client.post(f"/api/tasks/{task_id}/passport/generate")
    passport_id = passport_result.json()["id"]
    activation = client.post(f"/api/tasks/{task_id}/passport/activate")
    assert activation.status_code == 200
    session_result = client.post(f"/api/tasks/{task_id}/sessions")
    assert session_result.status_code == 201
    assert session_result.json()["passport_id"] == passport_id
    assert session_result.json()["status"] == "ACTIVE"
    return owner, session_result.json()["id"]


def post_action(client, session_id: str, tool_name: str, arguments: dict[str, object], **extra):
    return client.post(
        f"/api/sessions/{session_id}/actions",
        json={"tool_name": tool_name, "arguments": arguments, **extra},
    )


def test_clean_invoice_read_is_allowed_and_simulated(client, db_session) -> None:
    owner, session_id = create_active_session(client, db_session)

    result = post_action(
        client, session_id, "read_invoice",
        {"fixture_key": "supplier-invoice-clean"},
    )

    assert result.status_code == 200
    payload = result.json()
    assert payload["decision"]["outcome"] == "ALLOW"
    assert payload["decision"]["tool_executed"] is True
    assert payload["result"]["simulated"] is True
    assert payload["result"]["output"]["invoice"]["invoice_number"] == "SYN-INV-0042"
    assert payload["result"]["output"]["invoice"]["supplier"]["contact"].startswith("a***@")
    action = db_session.get(ActionRequest, payload["action_id"])
    assert action.organization_id == owner.organization_id
    assert action.source_trust == "TRUSTED"


def test_poisoned_invoice_read_is_allowed_but_records_untrusted_finding(
    client, db_session
) -> None:
    _, session_id = create_active_session(client, db_session)

    result = post_action(
        client, session_id, "read_invoice",
        {"fixture_key": "supplier-invoice-poisoned"},
    )

    assert result.status_code == 200
    payload = result.json()
    assert payload["decision"]["outcome"] == "ALLOW"
    assert payload["result"]["simulated"] is True
    assert db_session.scalar(
        select(PolicyDecision).where(
            PolicyDecision.action_request_id == payload["action_id"]
        )
    ).severity == "HIGH"
    assert payload["result"]["output"]["trust_level"] == "UNTRUSTED"
    assert "untrusted_instruction" in payload["result"]["output"]["invoice"]
    assert "archive@external-recipient.example.test" not in result.text
    assert payload["findings"][0]["category"] == "PROMPT_INJECTION"
    finding = db_session.scalar(
        select(DataFinding).where(
            DataFinding.action_request_id == payload["action_id"]
        )
    )
    assert finding is not None
    persisted_categories = set(
        db_session.scalars(
            select(DataFinding.category).where(
                DataFinding.action_request_id == payload["action_id"]
            )
        ).all()
    )
    assert {
        "PROMPT_INJECTION",
        "CUSTOMER_EMAIL",
        "PHONE_NUMBER",
        "GOVERNMENT_ID_LIKE",
        "CUSTOMER_LIST",
        "EXTERNAL_DATA_EXPOSURE",
        "DESTRUCTIVE_ACTION_REQUEST",
    } <= persisted_categories
    assert "customer-01@synthetic-customer.example.test" not in result.text
    assert "0000000000" not in result.text
    assert "0000 0000 0000" not in result.text
    assert "Synthetic Customer 01" not in result.text
    persisted_findings = db_session.scalars(
        select(DataFinding).where(
            DataFinding.action_request_id == payload["action_id"]
        )
    ).all()
    masked_text = " ".join(finding.masked_value for finding in persisted_findings)
    assert "c***@synthetic-customer.example.test" in masked_text
    assert "***-***-0000" in masked_text
    assert "XXXXXX0000" in masked_text
    assert "customer-01@synthetic-customer.example.test" not in masked_text
    assert "0000000000" not in masked_text
    assert "0000 0000 0000" not in masked_text
    action_audits = db_session.scalars(
        select(AuditEvent).where(AuditEvent.action_id == payload["action_id"])
    ).all()
    assert all(
        sensitive_value not in event.description + str(event.metadata_json)
        for event in action_audits
        for sensitive_value in (
            "customer-01@synthetic-customer.example.test",
            "0000000000",
            "0000 0000 0000",
            "Synthetic Customer 01",
        )
    )
    agent_session = db_session.get(AgentSession, session_id)
    assert agent_session.status == "ACTIVE"


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_outcome"),
    [
        (
            "delete_backup",
            {"backup_id": "synthetic-backup-daily-001"},
            "BLOCK",
        ),
        (
            "send_email",
            {
                "destination": "accounts@supplier.example.test",
                "template": "supplier_invoice_reminder",
            },
            "BLOCK",
        ),
        ("some_unknown_tool", {}, "BLOCKED_FAIL_CLOSED"),
        ("read_invoice", {"fixture_key": "..\\private.json"}, "BLOCKED_FAIL_CLOSED"),
        ("read_invoice", {"fixture_key": ["not", "a", "fixture"]}, "BLOCKED_FAIL_CLOSED"),
    ],
)
def test_non_allowed_actions_never_execute(
    client, db_session, monkeypatch, tool_name, arguments, expected_outcome
) -> None:
    _, session_id = create_active_session(client, db_session)

    def reject_execution(*args, **kwargs):
        _ = args, kwargs
        raise AssertionError("A denied action must never invoke a tool.")

    monkeypatch.setattr("app.services.enforcement_gateway.execute_tool", reject_execution)
    result = post_action(client, session_id, tool_name, arguments)

    assert result.status_code == 200
    assert result.json()["decision"]["outcome"] == expected_outcome
    assert result.json()["decision"]["tool_executed"] is False
    assert result.json()["result"] is None


def test_expired_passport_fails_closed(client, db_session) -> None:
    _, session_id = create_active_session(client, db_session)
    agent_session = db_session.get(AgentSession, session_id)
    db_session.execute(
        update(TaskPassport)
        .where(TaskPassport.id == agent_session.passport_id)
        .values(expires_at=utc_now() - timedelta(seconds=1))
    )
    db_session.expire_all()

    result = post_action(
        client, session_id, "read_invoice",
        {"fixture_key": "supplier-invoice-clean"},
    )

    assert result.status_code == 200
    assert result.json()["decision"]["outcome"] == "BLOCKED_FAIL_CLOSED"
    assert result.json()["decision"]["reason_code"] == "PASSPORT_EXPIRED"
    assert result.json()["decision"]["tool_executed"] is False


def test_missing_synthetic_source_context_fails_closed(client, db_session) -> None:
    _, session_id = create_active_session(client, db_session)
    db_session.query(SourceDocument).filter(
        SourceDocument.fixture_key == "supplier-invoice-clean"
    ).delete(synchronize_session=False)
    db_session.flush()

    result = post_action(
        client, session_id, "read_invoice",
        {"fixture_key": "supplier-invoice-clean"},
    )

    assert result.status_code == 200
    assert result.json()["decision"]["outcome"] == "BLOCKED_FAIL_CLOSED"
    assert result.json()["decision"]["reason_code"] == "SOURCE_CONTEXT_MISSING"
    assert result.json()["decision"]["tool_executed"] is False


@pytest.mark.parametrize(
    ("session_status", "reason_code"),
    [
        ("COMPLETED", "SESSION_NOT_ACTIVE"),
        ("QUARANTINED", "SESSION_QUARANTINED"),
    ],
)
def test_inactive_and_quarantined_sessions_fail_closed(
    client, db_session, session_status, reason_code
) -> None:
    _, session_id = create_active_session(client, db_session)
    db_session.get(AgentSession, session_id).status = session_status
    db_session.flush()

    result = post_action(
        client, session_id, "read_invoice",
        {"fixture_key": "supplier-invoice-clean"},
    )

    assert result.status_code == 200
    assert result.json()["decision"]["outcome"] == "BLOCKED_FAIL_CLOSED"
    assert result.json()["decision"]["reason_code"] == reason_code
    assert result.json()["decision"]["tool_executed"] is False


def test_another_organization_cannot_access_session(client, db_session) -> None:
    owner, session_id = create_active_session(client, db_session)
    other_organization = Organization(
        name="Synthetic Other Action Organization",
        environment="SYNTHETIC_DEMO",
        is_active=True,
    )
    db_session.add(other_organization)
    db_session.flush()
    original_session = db_session.get(AgentSession, session_id)
    original_session.organization_id = other_organization.id
    db_session.flush()

    result = post_action(
        client, session_id, "read_invoice",
        {"fixture_key": "supplier-invoice-clean"},
    )

    assert result.status_code == 404
    assert result.json()["code"] == "SESSION_NOT_FOUND"
    assert owner.organization_id != original_session.organization_id


def test_client_authorized_true_is_ignored(client, db_session) -> None:
    _, session_id = create_active_session(client, db_session)

    result = post_action(
        client,
        session_id,
        "delete_backup",
        {"backup_id": "synthetic-backup-daily-001"},
        authorized=True,
    )

    assert result.status_code == 200
    assert result.json()["decision"]["outcome"] == "BLOCK"
    assert result.json()["decision"]["tool_executed"] is False


def test_policy_is_committed_before_allowed_tool_execution(
    client, db_session, monkeypatch
) -> None:
    _, session_id = create_active_session(client, db_session)
    from app.tools import execute_tool as real_execute_tool

    def assert_policy_already_persisted(name, arguments):
        decision = db_session.scalar(
            select(PolicyDecision)
            .join(ActionRequest)
            .where(ActionRequest.session_id == session_id)
        )
        assert decision is not None
        assert decision.outcome == "ALLOW"
        assert decision.tool_executed is False
        return real_execute_tool(name, arguments)

    monkeypatch.setattr(
        "app.services.enforcement_gateway.execute_tool",
        assert_policy_already_persisted,
    )
    result = post_action(
        client, session_id, "read_invoice",
        {"fixture_key": "supplier-invoice-clean"},
    )

    assert result.status_code == 200
    assert result.json()["decision"]["tool_executed"] is True


def test_policy_decision_and_audit_event_are_persisted(client, db_session) -> None:
    _, session_id = create_active_session(client, db_session)

    result = post_action(
        client, session_id, "read_invoice",
        {"fixture_key": "supplier-invoice-clean"},
    )

    action_id = result.json()["action_id"]
    decision = db_session.scalar(
        select(PolicyDecision).where(
            PolicyDecision.action_request_id == action_id
        )
    )
    event = db_session.scalar(
        select(AuditEvent).where(AuditEvent.action_id == action_id)
    )
    assert decision is not None
    assert decision.outcome == "ALLOW"
    assert decision.tool_executed is True
    assert decision.tool_result_json is not None
    assert event is not None
    assert event.event_type == "ACTION_ALLOWED"
    assert event.organization_id == decision.organization_id
    assert "accounts@synthetic-coastal-cashew.example.test" not in (
        decision.tool_result_json
    )


def test_no_real_network_or_destructive_side_effect_occurs(
    client, db_session, monkeypatch, tmp_path: Path
) -> None:
    _, session_id = create_active_session(client, db_session)
    backup = tmp_path / "synthetic-backup-daily-001"
    backup.write_text("synthetic fixture backup", encoding="utf-8")

    def reject_side_effect(*args, **kwargs):
        _ = args, kwargs
        raise AssertionError("External or destructive side effect was attempted.")

    monkeypatch.setattr(socket, "create_connection", reject_side_effect)
    monkeypatch.setattr(socket.socket, "connect", reject_side_effect)
    monkeypatch.setattr(Path, "unlink", reject_side_effect)
    monkeypatch.setattr(os, "remove", reject_side_effect)
    monkeypatch.setattr(os, "unlink", reject_side_effect)

    email = post_action(
        client,
        session_id,
        "send_email",
        {
            "destination": "accounts@supplier.example.test",
            "template": "supplier_invoice_reminder",
        },
    )
    deletion = post_action(
        client,
        session_id,
        "delete_backup",
        {"backup_id": "synthetic-backup-daily-001"},
    )

    assert email.json()["decision"]["tool_executed"] is False
    assert deletion.json()["decision"]["tool_executed"] is False
    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == "synthetic fixture backup"


def test_poisoned_external_exposure_quarantines_and_creates_incident(
    client, db_session, monkeypatch
) -> None:
    owner, session_id = create_active_session(client, db_session)
    poisoned_document = db_session.scalar(
        select(SourceDocument).where(
            SourceDocument.organization_id == owner.organization_id,
            SourceDocument.fixture_key == "supplier-invoice-poisoned",
        )
    )

    def reject_execution(*args, **kwargs):
        _ = args, kwargs
        raise AssertionError("Unsafe external communication must not execute.")

    monkeypatch.setattr("app.services.enforcement_gateway.execute_tool", reject_execution)
    result = post_action(
        client,
        session_id,
        "send_email",
        {
            "destination": "archive@external-recipient.example.test",
            "template": "supplier_invoice_reminder",
        },
        source_document_id=poisoned_document.id,
    )

    assert result.status_code == 200
    response = result.json()
    assert response["decision"]["outcome"] == "BLOCK"
    assert response["decision"]["tool_executed"] is False
    assert "archive@external-recipient.example.test" not in result.text
    assert "EXTERNAL_DATA_EXPOSURE" in {
        finding["category"] for finding in response["findings"]
    }
    agent_session = db_session.get(AgentSession, session_id)
    assert agent_session.status == "QUARANTINED"
    incident = db_session.scalar(
        select(Incident).where(Incident.agent_session_id == session_id)
    )
    assert incident is not None
    assert incident.triggering_action_id == response["action_id"]
    assert incident.containment_status == "CONTAINED"
    notification = db_session.scalar(
        select(Notification).where(Notification.incident_id == incident.id)
    )
    assert notification is not None
    assert notification.channel == "MOCK"
    assert notification.status == "PENDING"
    assert "archive@external-recipient.example.test" not in (
        incident.summary + str(notification.last_error)
    )
    related_audits = db_session.scalars(
        select(AuditEvent).where(AuditEvent.incident_id == incident.id)
    ).all()
    assert all(
        "archive@external-recipient.example.test"
        not in (event.description + str(event.metadata_json))
        for event in related_audits
    )
    detail = client.get(f"/api/incidents/{incident.id}")
    assert "archive@external-recipient.example.test" not in detail.text


def test_destructive_request_quarantines_and_later_action_fails_closed(
    client, db_session, monkeypatch
) -> None:
    _, session_id = create_active_session(client, db_session)

    def reject_execution(*args, **kwargs):
        _ = args, kwargs
        raise AssertionError("Destructive tools must not execute.")

    monkeypatch.setattr("app.services.enforcement_gateway.execute_tool", reject_execution)
    deletion = post_action(
        client,
        session_id,
        "delete_backup",
        {"backup_id": "synthetic-backup-daily-001"},
    )
    assert deletion.status_code == 200
    assert deletion.json()["decision"]["outcome"] == "BLOCK"
    assert deletion.json()["decision"]["tool_executed"] is False
    assert db_session.get(AgentSession, session_id).status == "QUARANTINED"

    later_action = post_action(
        client,
        session_id,
        "read_invoice",
        {"fixture_key": "supplier-invoice-clean"},
    )
    assert later_action.status_code == 200
    assert later_action.json()["decision"]["outcome"] == "BLOCKED_FAIL_CLOSED"
    assert later_action.json()["decision"]["reason_code"] == "SESSION_QUARANTINED"
    assert later_action.json()["decision"]["tool_executed"] is False
    assert len(
        db_session.scalars(
            select(Incident).where(Incident.agent_session_id == session_id)
        ).all()
    ) == 1


def test_incident_review_does_not_reactivate_quarantined_session(
    client, db_session
) -> None:
    _, session_id = create_active_session(client, db_session)
    action = post_action(
        client,
        session_id,
        "delete_backup",
        {"backup_id": "synthetic-backup-daily-001"},
    )
    incident = db_session.scalar(
        select(Incident).where(
            Incident.triggering_action_id == action.json()["action_id"]
        )
    )
    assert incident is not None

    listed = client.get("/api/incidents")
    detail = client.get(f"/api/incidents/{incident.id}")
    acknowledged = client.post(
        f"/api/incidents/{incident.id}/acknowledge"
    )
    resolved = client.post(f"/api/incidents/{incident.id}/resolve")

    assert listed.status_code == 200
    assert any(item["id"] == incident.id for item in listed.json())
    assert detail.status_code == 200
    assert detail.json()["notifications"][0]["status"] == "PENDING"
    assert acknowledged.json()["owner_review_status"] == "REVIEWED"
    assert resolved.json()["owner_review_status"] == "RESOLVED"
    assert db_session.get(AgentSession, session_id).status == "QUARANTINED"


def test_another_organization_cannot_access_incident(client, db_session) -> None:
    owner, session_id = create_active_session(client, db_session)
    action = post_action(
        client,
        session_id,
        "delete_backup",
        {"backup_id": "synthetic-backup-daily-001"},
    )
    incident = db_session.scalar(
        select(Incident).where(
            Incident.triggering_action_id == action.json()["action_id"]
        )
    )
    other_organization = Organization(
        name="Synthetic Incident Isolation Organization",
        environment="SYNTHETIC_DEMO",
        is_active=True,
    )
    db_session.add(other_organization)
    db_session.flush()
    incident.organization_id = other_organization.id
    db_session.flush()

    result = client.get(f"/api/incidents/{incident.id}")

    assert result.status_code == 404
    assert result.json()["code"] == "INCIDENT_NOT_FOUND"
    assert owner.organization_id != other_organization.id


def test_unknown_fixture_integrity_context_fails_closed(client, db_session) -> None:
    owner, session_id = create_active_session(client, db_session)
    clean_document = db_session.scalar(
        select(SourceDocument).where(
            SourceDocument.organization_id == owner.organization_id,
            SourceDocument.fixture_key == "supplier-invoice-clean",
        )
    )
    clean_document.content_hash = "0" * 64
    db_session.flush()

    result = post_action(
        client,
        session_id,
        "read_invoice",
        {"fixture_key": "supplier-invoice-clean"},
    )

    assert result.status_code == 200
    assert result.json()["decision"]["outcome"] == "BLOCKED_FAIL_CLOSED"
    assert result.json()["decision"]["reason_code"] == "SOURCE_INSPECTION_FAILED"
    assert result.json()["decision"]["tool_executed"] is False


def test_incident_endpoints_require_authentication(client) -> None:
    paths = (
        ("get", "/api/incidents"),
        ("get", "/api/incidents/synthetic-incident-id"),
        ("post", "/api/incidents/synthetic-incident-id/acknowledge"),
        ("post", "/api/incidents/synthetic-incident-id/resolve"),
    )
    for method, path in paths:
        response = getattr(client, method)(path)
        assert response.status_code == 401
        assert response.json()["code"] == "UNAUTHENTICATED"


def test_action_arguments_and_destination_are_masked_in_storage_and_response(
    client, db_session
) -> None:
    _, session_id = create_active_session(client, db_session)

    result = post_action(
        client,
        session_id,
        "send_email",
        {
            "destination": "accounts@supplier.example.test",
            "template": "supplier_invoice_reminder",
        },
    )

    action = db_session.get(ActionRequest, result.json()["action_id"])
    assert "accounts@supplier.example.test" not in action.masked_arguments_json
    assert "a***@supplier.example.test" in action.masked_arguments_json
    assert action.destination == "a***@supplier.example.test"
    assert "accounts@supplier.example.test" not in result.text


def test_direct_tool_routes_do_not_exist(client) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert "/api/sessions/{session_id}/actions" in paths
    assert not any("/tools" in path for path in paths)
