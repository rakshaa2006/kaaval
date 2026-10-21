"""Tests for the endpoints used by the local frontend console."""
from __future__ import annotations

from pathlib import Path

from app.seed import seed_synthetic_data

FIXTURE_DIRECTORY = Path(__file__).resolve().parents[2] / "fixtures" / "invoices"


def authenticate(client, db_session) -> None:
    seed_synthetic_data(db_session, FIXTURE_DIRECTORY)
    response = client.post("/api/auth/demo-login")
    assert response.status_code == 200


def test_frontend_origins_support_credentialed_cors(client) -> None:
    for origin in (
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ):
        response = client.options(
            "/api/auth/me",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
        assert response.headers["access-control-allow-credentials"] == "true"


def test_console_api_supports_task_session_and_audit_flow(client, db_session) -> None:
    authenticate(client, db_session)

    created = client.post(
        "/api/tasks",
        json={"purpose": "Process synthetic invoice fixture and summarize the totals."},
    )
    assert created.status_code == 201
    task_id = created.json()["id"]

    task_list = client.get("/api/tasks")
    assert task_list.status_code == 200
    assert any(task["id"] == task_id for task in task_list.json())

    generated = client.post(f"/api/tasks/{task_id}/passport/generate")
    assert generated.status_code == 200
    assert generated.json()["allowed_tools"] == ["read_invoice"]

    activated = client.post(f"/api/tasks/{task_id}/passport/activate")
    assert activated.status_code == 200

    created_session = client.post(f"/api/tasks/{task_id}/sessions")
    assert created_session.status_code == 201
    session_id = created_session.json()["id"]

    session = client.get(f"/api/sessions/{session_id}")
    assert session.status_code == 200
    assert session.json()["task_id"] == task_id

    allowed_action = client.post(
        f"/api/sessions/{session_id}/actions",
        json={
            "tool_name": "read_invoice",
            "arguments": {"fixture_key": "supplier-invoice-clean"},
        },
    )
    assert allowed_action.status_code == 200
    assert allowed_action.json()["decision"]["outcome"] == "ALLOW"
    assert allowed_action.json()["decision"]["tool_executed"] is True
    assert allowed_action.json()["result"]["output"]["invoice"]["invoice_number"] == "SYN-INV-0042"

    blocked_action = client.post(
        f"/api/sessions/{session_id}/actions",
        json={
            "tool_name": "delete_backup",
            "arguments": {"backup_id": "synthetic-backup-demo-01"},
        },
    )
    assert blocked_action.status_code == 200
    assert blocked_action.json()["decision"]["outcome"] == "BLOCK"
    assert blocked_action.json()["decision"]["tool_executed"] is False

    timeline = client.get(f"/api/sessions/{session_id}/timeline")
    assert timeline.status_code == 200
    assert any(event["event_type"] == "SESSION_CREATED" for event in timeline.json())
    assert any(event["event_type"] == "ACTION_ALLOWED" for event in timeline.json())
    assert any(event["event_type"] == "ACTION_BLOCKED" for event in timeline.json())
    assert any(event["event_type"] == "INCIDENT_CREATED" for event in timeline.json())

    incidents = client.get("/api/incidents")
    assert incidents.status_code == 200
    assert any(incident["agent_session_id"] == session_id for incident in incidents.json())
    audit = client.get("/api/audit")
    assert audit.status_code == 200
    assert any(event["event_type"] == "TASK_CREATED" for event in audit.json())


def test_forbidden_email_and_destructive_actions_create_incidents(client, db_session) -> None:
    authenticate(client, db_session)

    prohibited_actions = (
        (
            "send_email",
            {
                "destination": "vendor@supplier.example.test",
                "template": "supplier_invoice_reminder",
            },
            "EXTERNAL_COMMUNICATION_FORBIDDEN",
        ),
        (
            "delete_backup",
            {"backup_id": "synthetic-backup-demo-01"},
            "DESTRUCTIVE_TOOL_FORBIDDEN",
        ),
    )
    for tool_name, arguments, expected_reason in prohibited_actions:
        created = client.post(
            "/api/tasks",
            json={"purpose": "Process synthetic invoice fixture."},
        )
        assert created.status_code == 201
        task_id = created.json()["id"]
        assert client.post(f"/api/tasks/{task_id}/passport/generate").status_code == 200
        activated = client.post(f"/api/tasks/{task_id}/passport/activate")
        assert activated.status_code == 200
        created_session = client.post(f"/api/tasks/{task_id}/sessions")
        assert created_session.status_code == 201
        session_id = created_session.json()["id"]

        action = client.post(
            f"/api/sessions/{session_id}/actions",
            json={"tool_name": tool_name, "arguments": arguments},
        )

        assert action.status_code == 200
        assert action.json()["decision"]["outcome"] == "BLOCK"
        assert action.json()["decision"]["reason_code"] == expected_reason
        assert action.json()["decision"]["tool_executed"] is False
        assert client.get(f"/api/sessions/{session_id}").json()["status"] == "QUARANTINED"
        timeline = client.get(f"/api/sessions/{session_id}/timeline")
        assert timeline.status_code == 200
        assert any(event["event_type"] == "ACTION_BLOCKED" for event in timeline.json())
        assert any(event["event_type"] == "INCIDENT_CREATED" for event in timeline.json())
        incidents = client.get("/api/incidents")
        assert any(
            incident["agent_session_id"] == session_id
            and incident["triggering_action_id"] == action.json()["action_id"]
            for incident in incidents.json()
        )


def test_console_api_keeps_session_and_audit_reads_authenticated(client) -> None:
    assert client.get("/api/tasks").status_code == 401
    assert client.get("/api/audit").status_code == 401
    assert client.get("/api/sessions/unknown").status_code == 401
    assert client.get("/api/sessions/unknown/timeline").status_code == 401
