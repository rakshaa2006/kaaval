Test Strategy
Kaaval testing must prove two things:

The normal product workflow works for the owner.

Unsafe or unauthorized agent behaviour cannot bypass the enforcement gateway.

Testing must cover the frontend, API, domain services, persistence, integrations, security boundaries, state transitions, audit trail, and synthetic Attack Lab.

The test strategy uses:

Unit tests for deterministic logic.

Integration tests for API, database, transactions, and adapters.

End-to-end tests for browser workflows.

Accessibility tests for keyboard and semantic behaviour.

Security tests for authentication, authorization, state integrity, and data leakage.

Regression tests for every audited correction.

Pytest fixtures should provide consistent test context and reusable setup, while parametrization should cover multiple policy and state combinations efficiently.

Playwright assertions should use async web-specific matchers so UI assertions wait for the expected state rather than relying on arbitrary delays.

Test Environments
Unit
No network.

In-memory or isolated database fixtures.

Mock clock where time affects expiry.

Mock notification and LLM adapters.

Deterministic policy inputs.

Integration
Test database.

FastAPI application client.

Mock external providers.

Real migrations.

Real transaction boundaries.

Synthetic fixtures only.

End-to-end
Running frontend.

Running backend.

Seeded synthetic organization and owner.

Mock LLM.

Mock Telegram.

Mock tools.

Browser automation with Playwright.

Staging smoke
HTTPS.

PostgreSQL-compatible database.

Synthetic data only.

Staging Telegram bot where configured.

Optional staging LLM adapter.

No real email or destructive tools.

Test Data
Organization
text
organization_id: org_demo
name: Mangaluru Cashew Traders
environment: SYNTHETIC_DEMO
Owner
text
role: OWNER_ADMIN
status: ACTIVE
email: owner@example.test
Tasks
Invoice summary task.

Empty task.

Cancelled task.

Expired task.

Restricted restart task.

Source documents
Clean supplier invoice.

Poisoned supplier invoice.

Invoice with synthetic customer email.

Invoice with phone number.

Invoice with government-ID-like value.

Invoice with customer list.

Invoice requesting unauthorized external transmission.

Destinations
Allowed synthetic supplier address.

Authorized internal address.

Unauthorized external address.

Missing destination.

Malformed destination.

Sessions
Active.

Waiting approval.

Completed.

Failed.

Expired.

Quarantined.

Approvals
Pending and valid.

Expired.

Already approved.

Already denied.

Mutated action.

Replayed callback.

Wrong owner.

Wrong organization.

Test Naming
Use names that express behaviour:

text
test_quarantined_session_cannot_execute_action
test_expired_passport_fails_closed
test_approval_cannot_be_replayed
test_safe_restart_creates_new_restricted_session
test_full_customer_email_is_not_persisted
Avoid vague names such as:

text
test_session
test_policy
test_api
Unit Test Plan
Authentication
Test:

Valid password authenticates.

Invalid password is rejected.

Inactive owner is rejected.

Unknown email is rejected.

Email normalization works.

Browser token is not stored in plaintext.

Expired browser session is rejected.

Revoked browser session is rejected.

Logout revokes the session.

Demo login works only in SYNTHETIC_DEMO.

Demo login is rejected in staging.

Authorization
Test:

Authenticated owner can access own organization.

User cannot access another organization’s task.

User cannot access another organization’s session.

User cannot access another organization’s incident.

Client-provided organization ID cannot broaden scope.

Unknown role cannot receive active permissions.

All protected service methods require authenticated organization context.

Security tests should explicitly cover authentication, authorization, and session management categories reflected in the OWASP Web Security Testing Guide.

Task State Machine
Test valid transitions:

text
PASSPORT_GENERATING → PASSPORT_REVIEW
PASSPORT_REVIEW → ACTIVE
ACTIVE → RUNNING
RUNNING → COMPLETED
RUNNING → FAILED
RUNNING → EXPIRED
Test invalid transitions:

Cancelled task to active.

Expired task to running.

Completed task to running.

Passport review to completed without session.

Task activation without active Passport.

Passport Compiler
Test:

Valid invoice purpose produces expected allowed tools.

Empty purpose fails.

Whitespace-only purpose fails.

Unknown tool is rejected.

Missing expiration is rejected.

Conflicting allow and deny rules are rejected.

Destructive tool is forbidden by default.

LLM output with extra fields is safely handled.

LLM output with invalid types is rejected.

LLM output requesting real email is rejected.

Document instruction cannot add tools.

Restricted restart Passport excludes email and deletion.

Activated Passport is immutable.

Regeneration creates a new version.

Previous active Passport becomes superseded where applicable.

Expired Passport cannot authorize actions.

Tool Registry
Test:

Known tools resolve.

Unknown tools fail closed.

read_invoice is classified as read-only.

send_email is classified as external communication.

delete_backup is classified as destructive.

Tool argument schemas reject malformed input.

Tool execution requires gateway-issued authorization context.

Direct adapter invocation is rejected or inaccessible.

Mock email has no network side effect.

Mock deletion does not delete a real file.

Context Inspector
Test detection of:

Synthetic customer email.

Synthetic phone number.

Government-ID-like value.

Customer list.

Prompt injection.

Multiple findings in one source.

Masked output.

Confidence and category fields.

Missing source context.

Untrusted document instructions.

Clean invoice with no findings.

Test context variation:

Local summary with customer email is allowed when Passport permits it.

External transmission of customer email is blocked.

Authorized supplier reminder may require approval.

Prompt injection requesting Passport expansion is blocked.

Prompt injection requesting backup deletion is blocked.

Policy Evaluator
Use parametrized tests for combinations of:

Session state.

Passport state.

Tool.

Source trust.

Data findings.

Destination.

Task purpose.

Approval rule.

Severity.

Expected outcomes:

text
ALLOW
REQUIRES_APPROVAL
BLOCK
BLOCKED_FAIL_CLOSED
Test:

Allowed invoice read.

Unauthorized email.

Destructive deletion.

Sensitive external exposure.

Missing destination.

Unknown tool.

Expired Passport.

Quarantined session.

Missing safety context.

Policy adapter failure.

Invalid action arguments.

Enforcement Gateway
Test the complete evaluation order:

Authentication.

Organization scope.

Task/session relationship.

Session state.

Passport state.

Tool registry.

Arguments.

Passport permissions.

Context inspection.

Data findings.

Policy outcome.

Persistence.

Quarantine when applicable.

Mock execution only after authorization.

Test:

Allowed action executes after decision persistence.

Blocked action does not execute.

Fail-closed action does not execute.

Execution result is persisted.

Audit event is persisted.

Request ID is propagated.

Sensitive values are masked before storage.

A gateway exception does not accidentally invoke a tool.

Approval Service
Test:

Approval created only for REQUIRES_APPROVAL.

Approval includes exact tool.

Approval includes exact arguments hash.

Approval includes exact destination.

Approval expires.

Valid approval executes once.

Denial does not execute.

Expired approval does not execute.

Already resolved approval does not execute.

Mutated arguments invalidate approval.

Mutated destination invalidates approval.

Wrong owner cannot resolve.

Wrong organization cannot resolve.

Replay is rejected.

Concurrent approval resolution results in one execution.

Sentinel
Test:

Severe blocked action quarantines session.

Repeated unsafe actions meet threshold and quarantine.

Quarantine is idempotent.

Existing quarantine is not overwritten incorrectly.

Quarantine creates incident.

Quarantine creates notification intent.

Quarantine writes audit events.

Quarantine prevents all later actions.

Notification failure does not unquarantine.

Incident resolution does not reactivate session.

Safe Restart
Test:

Restart requires quarantined original session.

Restart creates a new Passport.

New Passport has RESTRICTED_RESTART type.

New Passport allows only configured safe tools.

New Passport forbids email and deletion.

Restart creates a new session.

New session links to original session and incident.

Original session remains quarantined.

Restart cannot be performed twice unless explicitly supported.

Expired incident/task prevents restart.

Restart audit events are created.

Masking and Data Leakage
Test that full sensitive values do not appear in:

API response bodies.

Error responses.

Audit metadata.

Application logs.

Notification payloads.

Telegram message text.

Browser-visible technical details.

Attack Lab summaries.

Test masks for:

Email.

Phone.

Government-ID-like value.

Customer list.

Mixed-content strings.

Short values.

Repeated occurrences.

Notification Adapters
Test:

Mock notification succeeds.

Mock notification failure is persisted.

Retry updates status.

Telegram payload contains masked values.

Telegram secret header is required.

Wrong secret header is rejected.

Wrong chat ID is rejected.

Unknown approval ID is rejected.

Expired approval callback is rejected.

Replayed callback is rejected.

Valid callback resolves exact approval.

Notification success does not approve independently.

Notification failure does not resume session.

Audit Service
Test:

Required events are written.

Event fields are populated.

Related entity IDs are correct.

Events are ordered by server timestamp/event sequence.

Simulation events are marked.

Sensitive data is masked.

Normal API cannot update events.

Normal API cannot delete events.

Cross-organization events are inaccessible.

Transaction rollback removes events that should be atomic.

Attack Lab
Test:

Case list loads.

Baseline is simulation-only.

Baseline does not call real tools.

Protected run uses enforcement gateway.

Unauthorized email case is blocked.

Deletion case is blocked.

Prompt-injection case is blocked.

Repeated unsafe case quarantines the simulation session.

Benign case completes.

Results show simulation marker.

Simulation incidents cannot be mistaken for live incidents.

Reset removes only permitted synthetic records.

Reset requires confirmation.

Integration Test Plan
API Authentication
Test endpoints:

text
POST /api/auth/login
POST /api/auth/demo-login
POST /api/auth/logout
GET /api/auth/me
Verify:

Status codes.

Error envelope.

Cookie/token behaviour.

Request ID.

Expired session handling.

Demo-mode restriction.

API Task and Passport Flow
Test:

text
POST /api/tasks
POST /api/tasks/{task_id}/passport/generate
GET /api/tasks/{task_id}/passport
POST /api/tasks/{task_id}/passport/activate
Verify:

Task ownership.

State transitions.

Validation.

Polling status.

Regeneration.

Expiration.

Audit events.

Error mapping.

API Session Flow
Test:

text
POST /api/tasks/{task_id}/sessions
GET /api/sessions/{session_id}
GET /api/sessions/{session_id}/timeline
POST /api/sessions/{session_id}/actions
Verify:

Session requires active Passport.

Action requires matching task/session.

Action result is persisted.

Timeline includes findings and decisions.

Quarantined session rejects action.

Expired session rejects action.

Fail-closed response is correct.

API Incident Flow
Test:

text
GET /api/incidents
GET /api/incidents/{incident_id}
POST /api/incidents/{incident_id}/retry-notification
POST /api/incidents/{incident_id}/safe-restart
Verify:

Incident is visible after quarantine.

Notification state is visible.

Retry is safe and idempotent.

Safe restart creates new session.

Original session remains quarantined.

API Approval Flow
Test:

text
GET /api/approvals
POST /api/approvals/{approval_id}/resolve
POST /api/approvals/{approval_id}/retry-notification
Verify:

Pending approval appears.

Valid resolution executes exact action.

Denial does not execute.

Expiry is enforced server-side.

Replay returns appropriate error.

Audit events are created.

API Audit Flow
Test:

text
GET /api/audit
GET /api/audit/{event_id}
Verify:

Filters work.

Organization scope works.

Simulation filter works.

Related entity navigation IDs are correct.

Sensitive values remain masked.

End-to-End Test Plan
E2E-001 — Login
Steps
Open /login.

Enter seeded owner credentials.

Submit.

Confirm Dashboard appears.

Sign out.

Confirm Login appears.

Expected
Successful redirect.

No password in network response or DOM.

Logout invalidates protected requests.

E2E-002 — Create and Activate Passport
Steps
Login.

Select Create Task.

Enter invoice-summary purpose.

Generate Passport.

Review allowed, approval-required, and forbidden tools.

Activate Passport.

Expected
Task purpose is preserved.

Passport is visible.

delete_backup is forbidden.

Activation succeeds.

Dashboard or Task Details reflects active state.

E2E-003 — Allowed Invoice Read
Steps
Open active task.

Start protected session.

Wait for session monitor.

Observe read_invoice.

Open action details.

Expected
Action outcome is ALLOW.

Synthetic source is displayed.

Tool execution is recorded.

No sensitive full value is shown.

Audit event exists.

E2E-004 — Approval-Required Supplier Reminder
Steps
Start or use a task configured for supplier reminder.

Trigger simulated supplier reminder.

Open Approval Preview.

Review destination and masked content.

Approve.

Return to Session Monitor.

Expected
Approval is pending before resolution.

Exact action details are shown.

Approval executes once.

Action becomes approved/executed.

Approval cannot be reused.

E2E-005 — Blocked Poisoned Invoice
Steps
Start the poisoned invoice scenario.

Observe source trust and prompt-injection finding.

Observe attempted email or deletion.

Open action details.

Expected
Prompt injection is detected.

Unsafe action is blocked.

Mock tool does not execute.

Findings are masked.

Explanation states that document instructions cannot expand permissions.

E2E-006 — Quarantine
Steps
Trigger a severe unsafe action.

Observe Session Monitor.

Open Incident Details.

Return to original Session Monitor.

Attempt a new action through the UI/API.

Expected
Session becomes QUARANTINED.

Incident is created.

New actions are rejected.

Original session remains read-only.

Notification status is visible.

Notification failure does not resume the session.

E2E-007 — Safe Restart
Steps
Open quarantined Incident Details.

Select Start Safe Restart.

Review restrictions.

Confirm restricted session creation.

Open new Session Monitor.

Inspect original session.

Expected
New restricted Passport is shown.

Email and deletion remain disabled.

New session has a different ID.

Original session remains quarantined.

Audit links both sessions.

E2E-008 — Attack Lab
Steps
Open Attack Lab.

Confirm simulation banner.

Run attack suite.

Inspect baseline and protected results.

Open a case.

Reset simulation results.

Expected
Results are marked simulation.

Baseline does not execute real tools.

Protected results pass through the gateway.

Blocked and allowed outcomes match expectations.

Reset requires confirmation.

E2E-009 — Failure Recovery
Steps
Disable/mock API failure.

Load Dashboard.

Trigger Passport generation failure.

Trigger notification failure.

Restore service.

Retry.

Expected
Error states are understandable.

Retry actions appear where safe.

Entered task purpose is preserved.

Notification failure does not alter containment.

Server state is recovered after refresh.

Accessibility Test Plan
Keyboard
Test:

Login form.

Navigation.

Create Task.

Passport Review.

Approval Preview.

Safe Restart Review.

Incident Details.

Attack Lab reset dialog.

Verify:

All controls are reachable.

Focus order is logical.

Focus is visible.

Dialog focus is trapped.

Escape closes dismissible dialogs.

Focus returns to triggering control.

No essential action requires a pointer.

Screen reader
Verify labels and announcements for:

Page headings.

Form fields.

Error messages.

Status chips.

Session state changes.

Quarantine notification.

Approval resolution.

Notification failure.

Attack Lab completion.

Use semantic headings, labelled regions, and appropriate live regions.

Visual accessibility
Verify:

Text contrast.

Focus contrast.

Status differentiation without colour alone.

Text zoom to 200%.

Reflow at narrow viewport.

No clipped critical controls.

No hidden focus under sticky headers or dialogs.

WCAG 2.2 includes requirements for visible focus appearance and focus not being obscured, which are especially important for Kaaval’s approval and quarantine controls.

Reduced motion
Verify:

No required information depends on animation.

Quarantine state remains visible with reduced motion.

Loading has a textual status.

Motion is reduced when the OS preference is enabled.

Security Test Plan
Authentication
Brute-force response behaviour.

Invalid credential handling.

Session expiry.

Logout revocation.

Cookie security attributes.

Demo-login environment restriction.

No sensitive authentication data in logs.

Authorization
Cross-organization reads.

Cross-organization mutations.

Client role manipulation.

Client organization manipulation.

Direct endpoint access without UI.

Access after logout.

Access with expired session.

Access with revoked session.

Session management
Session fixation resistance.

Token rotation where applicable.

Session invalidation.

Quarantine cannot be bypassed by refresh.

Quarantine cannot be bypassed by direct API call.

Old session cannot be resumed through safe restart.

Concurrent state changes are consistent.

Tool security
Direct frontend-to-tool call unavailable.

Unknown tool rejected.

Tool arguments validated.

Tool execution requires gateway context.

Mock tools have no real side effects.

Deletion adapter cannot access filesystem outside fixture/test sandbox.

Email adapter cannot make network calls.

Approval security
Approval ID guessing.

Approval replay.

Approval expiry.

Approval mutation.

Wrong actor.

Wrong organization.

Concurrent approvals.

Forged Telegram callback.

Wrong webhook secret.

Wrong Telegram chat ID.

Data security
Full sensitive data absent from API.

Full sensitive data absent from audit.

Full sensitive data absent from notifications.

Full sensitive data absent from logs.

Raw prompt content not rendered unsafely.

Untrusted content is escaped.

No secrets in frontend bundle.

Abuse and resilience
Repeated unsafe actions trigger configured containment.

Notification outage does not weaken policy.

LLM outage fails closed where required.

Database error does not trigger tool execution.

Duplicate requests are idempotent where required.

Excessive polling does not create duplicate actions.

Performance Test Plan
V1 performance testing is modest but must identify obvious failure modes.

Measure:

Dashboard response time with seeded data.

Passport generation response time.

Action evaluation latency.

Approval resolution latency.

Audit timeline query time.

Attack Lab run time.

Polling load during active session.

Test:

1 active session.

5 concurrent sessions.

10 concurrent approval requests.

1000 audit events.

100 incidents.

Repeated dashboard polling.

Security decisions must remain correct under concurrency even if performance degrades.

Database and Migration Tests
Test:

Fresh database migration.

Migration from empty schema.

Seed data creation.

Foreign-key constraints.

Organization cascade behaviour.

Unique approval constraints.

Audit append-only constraints.

Safe restart relationships.

SQLite foreign-key enforcement.

PostgreSQL-compatible migration where available.

Reset ordering.

Rollback on failed transaction.

Mock Adapter Tests
Mock LLM
Test:

Valid Passport output.

Invalid structured output.

Unknown tool.

Over-broad permissions.

Timeout.

Service failure.

Malformed response.

Deterministic fallback.

Mock Telegram
Test:

Successful send.

Failed send.

Delayed send.

Retry.

Approval callback.

Duplicate callback.

Invalid callback.

Masking.

Mock tools
Test:

Successful invoice read.

Email record creation only.

Deletion record creation only.

No external network calls.

No real file deletion.

Tool result is linked to action request.

Regression Tests for Audited Corrections
The following tests are mandatory:

Correction	Regression test
No unsupported Tasks list	Navigation has no standalone Tasks list route
No unsupported Sessions list	Navigation has no standalone Sessions list route
Canonical states	Invalid state transitions are rejected
Safe restart semantics	New Passport and session are created
Original quarantine	Old session remains QUARANTINED
Reachable approval flow	Valid supplier reminder produces approval request
Source documents entity	Actions link to source document records
Notifications entity	Delivery attempts persist status
Context-aware privacy	Same value gets context-dependent outcomes
Polling V1	UI updates through polling without SSE requirement
Standard errors	API errors follow common envelope
Simulation baseline	Attack Lab baseline never calls real tools
Synthetic data	No production data or real side effects
Audit completeness	Full journey produces required audit events
Test Fixtures
Recommended fixtures:

text
authenticated_owner
inactive_owner
other_organization_owner
synthetic_organization
clean_invoice
poisoned_invoice
active_task
active_passport
expired_passport
active_session
quarantined_session
pending_approval
expired_approval
mock_telegram
mock_llm
mock_tool_registry
frozen_clock
test_database
api_client
browser_page
Pytest fixture scope should match resource lifetime. For example, database setup may be session- or module-scoped, while mutable workflow records should generally be function-scoped to prevent test coupling.

Test Execution
Local commands
Use the project’s existing commands after repository inspection. Expected examples:

text
pytest
pytest tests/unit
pytest tests/integration
pytest tests/security
pytest tests/e2e
playwright test
Do not assume these exact commands exist until the repository is inspected.

Test order
Lint and type checks.

Unit tests.

Integration tests.

Security tests.

Accessibility checks.

End-to-end tests.

Staging smoke tests.

Failure handling
A failed security or state-integrity test blocks release even if visual or non-critical tests pass.

Test Reporting
Each test run should report:

Commit or build identifier.

Environment.

Database type.

Mock/external adapter mode.

Test counts.

Passed/failed/skipped.

Security-test result.

E2E result.

Accessibility result.

Known limitations.

Artifact links for screenshots, traces, and logs where available.

Do not include sensitive fixture values in reports.

Release Gates
Functional gate
Primary journey passes.

Approval journey passes.

Quarantine journey passes.

Safe restart journey passes.

Attack Lab journey passes.

Error and retry states work.

Security gate
No direct tool bypass.

No cross-organization access.

No approval replay.

No quarantine bypass.

No full sensitive values in responses, logs, audits, or notifications.

No real email or deletion side effects.

Fail-closed behaviour passes.

Accessibility gate
Keyboard workflow passes.

Dialog focus passes.

Status announcements pass.

Contrast and focus checks pass.

Mobile reflow passes.

Reduced-motion behaviour passes.

Data gate
Synthetic-only fixtures.

Migration passes.

Audit records are present and masked.

Reset is environment-restricted.

No production credentials in source or frontend bundle.

Demo gate
Local demo starts from documented commands.

Seeded owner can authenticate.

Mock LLM and Telegram work without credentials.

Attack Lab is repeatable.

Dashboard and incident flow are understandable without technical explanation.

Final Acceptance Checklist
Repository stack inspected before implementation.

Unit test suite passes.

Integration test suite passes.

E2E primary journey passes.

Approval-required workflow is reachable.

Allowed invoice read executes.

Unauthorized email is blocked.

Backup deletion is blocked.

Prompt injection is detected.

Sensitive values are masked.

Severe action quarantines the session.

Notification failure preserves containment.

Original quarantined session never resumes.

Safe restart creates a new restricted Passport.

New session has restricted permissions.

Audit timeline explains the complete flow.

Attack Lab baseline is simulation-only.

API errors use the standard envelope.

Polling updates UI state correctly.

Keyboard and dialog workflows pass.

No real external side effects occur.

Synthetic demo reset is safe and environment-restricted.