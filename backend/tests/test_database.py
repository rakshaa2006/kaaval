"""Database schema, relationship, tenancy, and audit persistence tests."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine, delete, inspect, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.audit.service import append_audit_event
from app.db.base import upgrade_sqlite_schema
from app.models import (
    ActionRequest,
    AgentSession,
    AuthSession,
    ApprovalRequest,
    AttackCase,
    AttackRun,
    AuditEvent,
    DataFinding,
    Incident,
    Notification,
    Organization,
    PolicyDecision,
    SourceDocument,
    Task,
    TaskPassport,
    User,
)


EXPECTED_TABLES = {
    "organizations",
    "users",
    "auth_sessions",
    "tasks",
    "task_passports",
    "source_documents",
    "agent_sessions",
    "action_requests",
    "policy_decisions",
    "data_findings",
    "approval_requests",
    "notifications",
    "incidents",
    "audit_events",
    "attack_runs",
    "attack_cases",
}


def test_create_schema_includes_all_core_entities(engine) -> None:
    inspector = inspect(engine)
    assert EXPECTED_TABLES <= set(inspector.get_table_names())
    for table_name in EXPECTED_TABLES - {"organizations"}:
        assert "organization_id" in {
            column["name"] for column in inspector.get_columns(table_name)
        }

    index_columns = {
        table_name: {
            column
            for index in inspector.get_indexes(table_name)
            for column in index["column_names"]
        }
        for table_name in EXPECTED_TABLES
    }
    assert "task_id" in index_columns["agent_sessions"]
    assert "session_id" in index_columns["action_requests"]
    assert "incident_id" in index_columns["notifications"]
    assert "created_at" in index_columns["tasks"]
    assert "occurred_at" in index_columns["audit_events"]


def test_sqlite_foreign_keys_are_enabled(engine) -> None:
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1


def test_sqlite_upgrade_adds_missing_user_status_without_losing_data() -> None:
    legacy_engine = create_engine("sqlite:///:memory:")
    try:
        with legacy_engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE users (id VARCHAR(36) PRIMARY KEY, "
                    "email VARCHAR(320) NOT NULL)"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO users (id, email) "
                    "VALUES ('synthetic-user-id', 'legacy@example.test')"
                )
            )

        upgrade_sqlite_schema(legacy_engine)
        upgrade_sqlite_schema(legacy_engine)

        with legacy_engine.connect() as connection:
            user = connection.execute(
                text("SELECT id, email, status FROM users")
            ).one()
            assert user == ("synthetic-user-id", "legacy@example.test", "ACTIVE")
    finally:
        legacy_engine.dispose()


def test_lifecycle_states_reject_contradictory_values(db_session: Session) -> None:
    organization = Organization(name="Synthetic Lifecycle Org")
    db_session.add(organization)
    db_session.flush()
    owner = User(
        organization_id=organization.id,
        email="lifecycle-owner@example.test",
        password_hash="synthetic-test-hash",
    )
    db_session.add(owner)
    db_session.flush()
    task = Task(
        organization_id=organization.id,
        owner_id=owner.id,
        purpose="Synthetic lifecycle test.",
    )
    db_session.add(task)
    db_session.flush()
    passport = TaskPassport(
        task_id=task.id,
        organization_id=organization.id,
        purpose=task.purpose,
    )
    db_session.add(passport)
    db_session.flush()

    invalid_records = (
        Task(
            organization_id=organization.id,
            owner_id=owner.id,
            purpose="Synthetic task.",
            status="PASSPORT_GENERATION_FAILED",
        ),
        TaskPassport(
            task_id=task.id,
            organization_id=organization.id,
            purpose=task.purpose,
            activation_status="GENERATED",
        ),
        AgentSession(
            organization_id=organization.id,
            task_id=task.id,
            passport_id=passport.id,
            owner_id=owner.id,
            status="WAITING_FOR_APPROVAL",
        ),
    )
    for record in invalid_records:
        with pytest.raises(IntegrityError):
            with db_session.begin_nested():
                db_session.add(record)
                db_session.flush()


def test_core_relationships_and_organization_scope(db_session: Session) -> None:
    first_org = Organization(name="Synthetic Org One")
    second_org = Organization(name="Synthetic Org Two")
    db_session.add_all([first_org, second_org])
    db_session.flush()

    owner = User(
        organization_id=first_org.id,
        email="owner-one@example.test",
        password_hash="synthetic-test-hash",
    )
    other_owner = User(
        organization_id=second_org.id,
        email="owner-two@example.test",
        password_hash="synthetic-test-hash",
    )
    db_session.add_all([owner, other_owner])
    db_session.flush()

    task = Task(
        organization_id=first_org.id,
        owner_id=owner.id,
        purpose="Summarize synthetic invoice data.",
    )
    other_task = Task(
        organization_id=second_org.id,
        owner_id=other_owner.id,
        purpose="Review synthetic records.",
    )
    db_session.add_all([task, other_task])
    db_session.flush()

    auth_session = AuthSession(
        user_id=owner.id,
        organization_id=first_org.id,
        token_hash="a" * 64,
        expires_at=datetime.now() + timedelta(hours=1),
    )
    source_document = SourceDocument(
        organization_id=first_org.id,
        fixture_key="synthetic-invoice",
        content_hash="b" * 64,
    )
    db_session.add_all([auth_session, source_document])
    db_session.flush()

    passport = TaskPassport(
        task_id=task.id,
        organization_id=first_org.id,
        purpose=task.purpose,
    )
    db_session.add(passport)
    db_session.flush()

    agent_session = AgentSession(
        organization_id=first_org.id,
        task_id=task.id,
        passport_id=passport.id,
        owner_id=owner.id,
    )
    db_session.add(agent_session)
    db_session.flush()

    action = ActionRequest(
        organization_id=first_org.id,
        task_id=task.id,
        session_id=agent_session.id,
        request_id="synthetic-request-1",
        tool_name="read_invoice",
        masked_arguments_json="{}",
        source_document_id=source_document.id,
    )
    db_session.add(action)
    db_session.flush()

    decision = PolicyDecision(
        action_request_id=action.id,
        organization_id=first_org.id,
        outcome="ALLOW",
        policy_reason="Synthetic test decision.",
        plain_reason="Synthetic action permitted.",
    )
    db_session.add(decision)

    finding = DataFinding(
        action_request_id=action.id,
        organization_id=first_org.id,
        category="CUSTOMER_EMAIL",
        masked_value="a***@example.test",
    )
    approval = ApprovalRequest(
        action_request_id=action.id,
        organization_id=first_org.id,
        owner_id=owner.id,
        action_binding_hash="c" * 64,
        policy_reason="Synthetic test approval.",
        expires_at=datetime.now() + timedelta(minutes=5),
    )
    db_session.add_all([finding, approval])
    db_session.flush()

    incident = Incident(
        organization_id=first_org.id,
        agent_session_id=agent_session.id,
        triggering_action_id=action.id,
        summary="Synthetic test incident.",
    )
    db_session.add(incident)
    db_session.flush()

    notification = Notification(
        organization_id=first_org.id,
        incident_id=incident.id,
        approval_request_id=approval.id,
        notification_type="APPROVAL_REQUEST",
    )
    db_session.add(notification)

    attack_run = AttackRun(
        organization_id=first_org.id,
        initiated_by_id=owner.id,
    )
    db_session.add(attack_run)
    db_session.flush()

    attack_case = AttackCase(
        organization_id=first_org.id,
        attack_run_id=attack_run.id,
        case_key="synthetic-case",
        expected_outcome="BLOCK",
    )
    db_session.add(attack_case)
    db_session.flush()

    assert task.organization.id == first_org.id
    assert task.owner.id == owner.id
    assert first_org.users == [owner]
    assert passport.task.id == task.id
    assert task.passports == [passport]
    assert agent_session.task.id == task.id
    assert task.agent_sessions == [agent_session]
    assert agent_session.passport.id == passport.id
    assert agent_session.action_requests == [action]
    assert action.agent_session.id == agent_session.id
    assert action.source_document.fixture_key == source_document.fixture_key
    assert action.policy_decision.id == decision.id
    assert action.data_findings == [finding]
    assert action.approval_request.id == approval.id
    assert approval.owner.id == owner.id
    assert auth_session.user.id == owner.id
    assert auth_session.organization.id == first_org.id
    assert incident.agent_session.id == agent_session.id
    assert incident.triggering_action_id == action.id
    assert incident.notifications == [notification]
    assert notification.organization.id == first_org.id
    assert notification.incident.id == incident.id
    assert attack_run.cases == [attack_case]
    assert attack_case.organization.id == first_org.id
    scoped_tasks = db_session.scalars(
        select(Task).where(Task.organization_id == first_org.id)
    ).all()
    assert scoped_tasks == [task]
    assert first_org.tasks == [task]
    assert second_org.tasks == [other_task]
    assert first_org.notifications == [notification]
    assert first_org.audit_events == []


def test_audit_service_rejects_bulk_update(db_session: Session) -> None:
    organization = Organization(name="Synthetic Audit Org")
    db_session.add(organization)
    db_session.flush()
    append_audit_event(
        db_session,
        organization_id=organization.id,
        event_type="TASK_CREATED",
        actor_type="SYSTEM",
        description="Synthetic test event.",
    )
    db_session.flush()

    with pytest.raises(ValueError, match="cannot be updated or deleted"):
        db_session.execute(
            update(AuditEvent).values(description="Attempted bulk mutation.")
        )
    db_session.rollback()


def test_audit_service_rejects_bulk_delete(db_session: Session) -> None:
    organization = Organization(name="Synthetic Audit Org")
    db_session.add(organization)
    db_session.flush()
    append_audit_event(
        db_session,
        organization_id=organization.id,
        event_type="TASK_CREATED",
        actor_type="SYSTEM",
        description="Synthetic test event.",
    )
    db_session.flush()

    with pytest.raises(ValueError, match="cannot be updated or deleted"):
        db_session.execute(delete(AuditEvent))
    db_session.rollback()


def test_organization_scoped_records_reject_unknown_organization(db_session: Session) -> None:
    task = Task(
        organization_id="00000000-0000-0000-0000-000000000001",
        owner_id="00000000-0000-0000-0000-000000000002",
        purpose="Synthetic task.",
    )
    db_session.add(task)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_audit_service_appends_events_and_rejects_updates(db_session: Session) -> None:
    organization = Organization(name="Synthetic Audit Org")
    db_session.add(organization)
    db_session.flush()

    audit_event = append_audit_event(
        db_session,
        organization_id=organization.id,
        event_type="TASK_CREATED",
        actor_type="SYSTEM",
        description="Synthetic test event.",
    )
    db_session.flush()
    assert audit_event.id is not None
    assert organization.audit_events == [audit_event]

    audit_event.description = "Attempted synthetic mutation."
    with pytest.raises(ValueError, match="cannot be updated"):
        db_session.flush()
    db_session.rollback()


def test_audit_service_rejects_deletes(db_session: Session) -> None:
    organization = Organization(name="Synthetic Audit Org")
    db_session.add(organization)
    db_session.flush()
    audit_event = append_audit_event(
        db_session,
        organization_id=organization.id,
        event_type="TASK_CREATED",
        actor_type="SYSTEM",
        description="Synthetic test event.",
    )
    db_session.flush()

    db_session.delete(audit_event)
    with pytest.raises(ValueError, match="cannot be deleted"):
        db_session.flush()
    db_session.rollback()
