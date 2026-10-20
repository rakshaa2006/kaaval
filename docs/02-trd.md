Kaaval is a modular monolith that places a backend enforcement gateway between an AI agent and protected tools.

text
React frontend
      ↓
FastAPI API
      ↓
Application services
      ├── Authentication and authorization
      ├── Task Passport compiler
      ├── Policy enforcement gateway
      ├── Context-aware data inspector
      ├── Mock tool executor
      ├── Approval service
      ├── Kaaval Sentinel
      ├── Notification adapters
      ├── Audit service
      └── Attack Lab simulator
      ↓
Relational database
The agent may propose a tool action, but the backend independently decides whether that action can execute. This follows least-agency and least-privilege principles: agents should receive only the tools and authority required for a particular task and duration.

Technical Goals
The V1 system must:

Enforce task-scoped permissions.

Fail closed when safety evaluation is unavailable.

Keep the frontend outside the protected-tool trust boundary.

Keep all data synthetic.

Prevent real email and deletion side effects.

Record security decisions and interventions.

Support a reliable local demo without external services.

Support staging deployment with PostgreSQL-compatible persistence.

Provide clear loading, empty, error, and success states.

Keep quarantined sessions from resuming.

Non-Goals
V1 does not require:

Microservices.

Kubernetes.

Real business-system integrations.

Real email delivery.

Real backup deletion.

User-upload workflows.

Multiple active roles.

Distributed agent orchestration.

Fully autonomous incident recovery.

SSE or WebSocket streaming.

Production compliance certification.

Technology Stack
Frontend
React.

TypeScript.

Vite.

Tailwind CSS or the existing project’s equivalent styling system.

React Router or the existing project router.

Playwright for browser tests.

Use the existing project stack if one exists. Do not replace a working stack unless required by this document.

Backend
Python 3.12 or the existing supported Python version.

FastAPI.

Pydantic.

SQLAlchemy or SQLModel.

Pytest.

HTTPX for API tests.

FastAPI supports relational databases through SQLAlchemy-compatible layers, including SQLite and PostgreSQL, which supports the planned local SQLite and staging PostgreSQL-compatible environments.

Database
SQLite for local development and offline demo.

PostgreSQL-compatible database for staging.

Migration tool compatible with the selected ORM.

Foreign-key enforcement enabled in local development.

External Adapters
Telegram Bot API for optional notifications and approvals.

Optional LLM adapter for Passport generation and ambiguous classification.

Deterministic mock adapters for local development and fallback.

Telegram API requests must use HTTPS, and webhook requests must be validated using Telegram’s configured secret token/header.

Runtime Environments
SYNTHETIC_DEMO
Required local environment.

Characteristics:

Synthetic invoice data only.

Seeded owner account.

Demo-login shortcut may be enabled.

Mock LLM compiler available.

Mock Telegram adapter available.

No real external side effects.

Demo reset permitted.

STAGING
Characteristics:

PostgreSQL-compatible database.

HTTPS.

Password authentication.

Separate Telegram bot.

Separate LLM credentials.

Synthetic data only.

Demo reset restricted to authorized owner/admin action.

Production
Production is outside V1 scope. The architecture should avoid blocking future production hardening but must not claim production readiness.

Repository Inspection Requirement
Before implementation:

Inspect the existing repository.

Identify frontend and backend entry points.

Identify package managers and commands.

Identify existing routes and components.

Identify database models and migrations.

Identify environment handling.

Run the existing test suite.

Reuse established conventions where compatible.

No new framework or folder structure should be introduced until the inspection is complete.

Authentication and Sessions
Human authentication
V1 contains one seeded owner/admin:

text
role = OWNER_ADMIN
Authentication requirements:

Store password hashes, never plaintext passwords.

Normalize email to lowercase.

Store opaque browser tokens as hashes.

Set session expiry.

Revoke sessions on logout.

Reject inactive users.

Scope all API operations by organization.

A synthetic demo-login endpoint may exist only when the environment is SYNTHETIC_DEMO.

Browser session
A browser session authorizes dashboard/API access for the human owner. It does not directly authorize agent tool execution.

Required properties:

Unique session ID.

Hashed token.

User ID.

Creation timestamp.

Last-seen timestamp.

Expiration timestamp.

Optional revocation timestamp.

Agent session
An agent session is separate from a browser session.

It must be bound to:

Organization.

Task.

Active Passport.

Initiating owner.

Optional parent session for safe restart.

The agent session status is one of:

text
STARTING
ACTIVE
WAITING_APPROVAL
COMPLETED
FAILED
EXPIRED
QUARANTINED
A quarantined session cannot return to ACTIVE.

Authorization Model
Organization scope
Every protected query and mutation must include organization scope.

Do not rely only on a client-provided organization ID. Derive the organization from the authenticated user and verify that all referenced records belong to the same organization.

V1 role
Only OWNER_ADMIN is active.

Future role values may be reserved in code, but they must not receive undocumented permissions.

Permission principles
Default deny.

Task-scoped tool access.

Passport-scoped data constraints.

Short-lived Passport expiration.

Explicit authorization for sensitive actions.

Fresh approval for the exact tool call, arguments, destination, and target.

No approval reuse after consumption or mutation.

Approval must be checked and consumed atomically immediately before execution. A client-provided user_confirmed flag is never sufficient.

Task Passport
A Task Passport is an immutable, versioned permission set for one task.

Passport contents
Task purpose.

Allowed tools.

Forbidden tools.

Data constraints.

Approval rules.

Expiration.

Passport type.

Generation status.

Activation status.

Optional model metadata.

Passport types
text
STANDARD
RESTRICTED_RESTART
Passport generation
V1 must provide a deterministic compiler for the invoice workflow.

Optional LLM generation may be added through an adapter, but LLM output must be:

Parsed as structured data.

Validated with Pydantic.

Checked against the tool registry.

Checked for permission contradictions.

Rejected if invalid or incomplete.

An LLM cannot activate a Passport or override deterministic authorization.

Passport activation
Activation is transactional:

Lock task and Passport.

Verify task is not cancelled.

Verify Passport is valid.

Verify expiration exists.

Validate tools and rules.

Ensure only one active Passport exists for the task.

Activate Passport.

Update task state.

Append audit event.

Commit.

Tool Registry
The backend maintains a registry of known tools.

read_invoice
Type: read.

Side effect: none.

Default Passport access: allowed for invoice-summary task.

Required context: source document and task purpose.

Data restrictions: synthetic invoice data only.

send_email
Type: external communication.

Side effect: simulated only.

Default Passport access: forbidden unless explicitly configured.

Approval example: legitimate supplier reminder with allowed destination and no sensitive data.

Block conditions: unauthorized destination, sensitive outbound data, suspicious source instruction, destructive intent.

delete_backup
Type: destructive.

Side effect: simulated only.

Default Passport access: forbidden.

V1 invoice workflow: always blocked.

Tool execution boundary
Mock tools must not be callable directly from the frontend or an untrusted agent process. Every execution must pass through the enforcement gateway.

Action Enforcement Gateway
Action input
Every action request contains:

Organization ID from authenticated context.

Task ID.

Session ID.

Tool name.

Arguments.

Masked arguments for storage.

Destination, when applicable.

Source document reference, when applicable.

Source trust.

Purpose context.

Request ID.

Evaluation order
Authenticate request.

Resolve organization from authenticated principal.

Validate task/session relationship.

Validate session is executable.

Validate Passport is active and unexpired.

Validate tool exists in registry.

Validate argument schema.

Check Passport tool permission.

Inspect source and destination context.

Detect sensitive findings.

Apply deterministic policy.

Persist action, findings, decision, and audit event.

If severe, quarantine and create incident in the same transaction.

Execute a mock tool only after a committed allow or consumed approval.

Persist execution result and audit event.

Outcomes
text
ALLOW
REQUIRES_APPROVAL
BLOCK
BLOCKED_FAIL_CLOSED
Fail-closed rules
Return BLOCKED_FAIL_CLOSED when:

Passport cannot be loaded.

Passport is invalid or expired.

Session state cannot be verified.

Tool is unknown.

Required context is missing.

Safety inspection is unavailable.

Policy evaluation errors.

Approval cannot be atomically consumed.

External destination cannot be validated.

Context-Aware Privacy Inspection
Inputs
The inspector evaluates:

Task purpose.

Source document.

Source trust level.

Document content classification.

Tool name.

Arguments.

Destination.

Passport data constraints.

Approval rules.

Detected findings.

V1 finding types
text
CUSTOMER_EMAIL
PHONE_NUMBER
GOVERNMENT_ID_LIKE
CUSTOMER_LIST
PROMPT_INJECTION
Finding requirements
Store only:

Finding category.

Masked value.

Location hint.

Confidence.

Detector.

Recommended action.

Source/action reference.

Do not store full sensitive values.

Context-sensitive example
A customer email may be:

Allowed for local invoice summarization.

Approval-required for an approved internal supplier reminder.

Blocked for an unauthorized external destination.

Blocked when extracted from a prompt-injection instruction requesting data exfiltration.

Session Quarantine
Trigger
Quarantine may be triggered by:

Destructive action attempt.

Sensitive-data exfiltration attempt.

Repeated unauthorized actions.

High-confidence prompt injection combined with a dangerous request.

Policy engine severity threshold.

Transaction
The quarantine transaction must:

Lock the session.

Confirm it is not already quarantined.

Set session status to QUARANTINED.

Store reason and timestamp.

Create or link the incident.

Append action and quarantine audit events.

Create notification record.

Commit.

No later action from that session may execute.

Incident Management
Incident statuses
Use separate fields rather than conflating session and incident state:

text
containment_status:
PENDING
CONTAINED
FAILED

owner_review_status:
OPEN
REVIEWED
RESOLVED

recovery_status:
NOT_STARTED
RESTRICTED_RESTART_CREATED
NOT_AVAILABLE
Closing an incident does not reactivate a session.

Notification status
text
PENDING
SENT
FAILED
RETRYING
Notification rules
Persist notification intent before attempting delivery.

Record attempts and failures.

Retry only through an explicit safe operation.

Never interpret notification success as action approval.

Never interpret notification failure as a reason to resume a session.

Approval Workflow
Approval creation
An approval request is created only for a policy result of REQUIRES_APPROVAL.

It is linked to exactly one action request and one owner.

Approval resolution
The resolution transaction must:

Lock approval and action.

Verify status is PENDING.

Verify current time is before expiry.

Verify the approving owner.

Verify action parameters and destination match the approved request.

Mark approval consumed/resolved.

Append audit event.

Commit.

Execute the exact approved mock action.

If any check fails, do not execute.

Telegram callback
Telegram callbacks must validate:

Webhook secret header.

Telegram chat ID.

Approval ID.

Callback signature or server-side lookup token.

Approval expiry.

Approval status.

Exact action binding.

Replay protection.

Telegram’s Bot API supports a webhook secret_token, delivered through the X-Telegram-Bot-Api-Secret-Token header.

API Surface
Health
text
GET /api/health
GET /api/ready
Authentication
text
POST /api/auth/login
POST /api/auth/demo-login       # synthetic mode only
POST /api/auth/logout
GET  /api/auth/me
Tasks and Passports
text
POST /api/tasks
GET  /api/tasks/{task_id}
POST /api/tasks/{task_id}/passport/generate
GET  /api/tasks/{task_id}/passport
POST /api/tasks/{task_id}/passport/activate
POST /api/tasks/{task_id}/passport/regenerate
POST /api/tasks/{task_id}/cancel
Sessions and Actions
text
POST /api/tasks/{task_id}/sessions
GET  /api/sessions/{session_id}
GET  /api/sessions/{session_id}/timeline
POST /api/sessions/{session_id}/actions
POST /api/sessions/{session_id}/quarantine
The frontend polls GET /api/sessions/{session_id} and the timeline endpoint during active execution.

Approvals
text
GET  /api/approvals
POST /api/approvals/{approval_id}/resolve
POST /api/approvals/{approval_id}/retry-notification
Incidents
text
GET  /api/incidents
GET  /api/incidents/{incident_id}
POST /api/incidents/{incident_id}/retry-notification
POST /api/incidents/{incident_id}/safe-restart
Telegram
text
POST /api/integrations/telegram/webhook
Audit
text
GET /api/audit
GET /api/audit/{event_id}
Attack Lab
text
GET  /api/attack-lab/cases
POST /api/attack-lab/runs
GET  /api/attack-lab/runs/{run_id}
POST /api/attack-lab/reset
Dashboard
text
GET /api/dashboard
API Error Contract
All errors use:

json
{
  "code": "SESSION_QUARANTINED",
  "message": "This session is quarantined and cannot execute new actions.",
  "details": {},
  "request_id": "req_123"
}
Required error codes:

text
UNAUTHENTICATED
FORBIDDEN
NOT_FOUND
VALIDATION_ERROR
PASSPORT_INVALID
PASSPORT_EXPIRED
SESSION_QUARANTINED
ACTION_BLOCKED
APPROVAL_EXPIRED
APPROVAL_ALREADY_RESOLVED
SAFETY_CHECK_UNAVAILABLE
NOTIFICATION_FAILED
INTERNAL_ERROR
Do not return raw stack traces, secrets, raw prompts, or full sensitive values.

Polling and Consistency
V1 uses polling rather than SSE or WebSockets.

Recommended behaviour:

Poll every 2–5 seconds while a session is active.

Stop aggressive polling after completion, failure, expiry, or quarantine.

Poll incident notification status while a retry is in progress.

Use server timestamps and event IDs for ordering.

On reconnect, fetch the complete current server state rather than attempting client-side replay.

Database and Transactions
Required atomic operations
Task creation
Create task and audit event together.

Passport activation
Activate Passport, update task state, and write audit event together.

Action evaluation
Persist action request, findings, decision, and audit events together.

Quarantine
Update session, create incident, create notification intent, and write audit events together.

Approval resolution
Consume approval exactly once and bind it to the exact action.

Safe restart
Create restricted Passport and new session while preserving the quarantined original.

Isolation
Use database transactions and row locks where supported. For SQLite, implement application-level guards and test duplicate/concurrent requests.

File and Fixture Storage
V1 uses local seeded fixture files.

Example:

text
fixtures/
  invoices/
    supplier-invoice-clean.json
    supplier-invoice-poisoned.json
The database stores a source_documents.fixture_key, content hash, trust level, and synthetic flag.

No upload endpoint or upload UI is required.

Audit and Logging
Audit event requirements
Audit records are append-only and organization-scoped.

Events must include:

Event type.

Actor type.

Optional actor ID.

Related task/session/action/incident/approval IDs.

Decision and reason where relevant.

Masked metadata.

Simulation flag.

Server timestamp.

Application logs
Logs may include:

Request ID.

Route.

Latency.

Status code.

Error code.

Record IDs.

Logs must not include:

Passwords.

Session tokens.

Telegram bot token.

Full invoice content.

Full sensitive values.

Raw external approval payloads.

Security Controls
Required
Secure password hashing.

Hashed browser tokens.

Organization-scoped queries.

Default-deny tool access.

Server-side authorization.

Exact approval binding.

Approval expiry and replay protection.

Fail-closed enforcement.

Masking before persistence.

Telegram webhook secret validation.

HTTPS for staging integrations.

Mock-only destructive tools.

No direct frontend-to-tool calls.

No client-controlled authorization decisions.

Optional after V1
Signed task-scoped authorization tokens.

Policy-as-code engine such as OPA or Cedar.

Hardware-backed secrets.

Fine-grained multi-role permissions.

Distributed worker isolation.

Testing Strategy
Unit tests
Passport validation.

Tool registry.

State transitions.

Data finding masking.

Context policy rules.

Error mapping.

Notification adapters.

Attack Lab case definitions.

Integration tests
Authentication and organization scope.

Task and Passport lifecycle.

Enforcement gateway.

Approval transaction.

Quarantine and incident creation.

Safe restart.

Audit persistence.

Telegram webhook validation.

End-to-end tests
Primary journey:

Login.

Create task.

Generate Passport.

Activate Passport.

Start session.

Allow invoice read.

Block poisoned email/deletion.

Quarantine.

Review incident.

Safe restart.

Complete restricted task.

Review audit.

Run Attack Lab.

Security tests
Direct tool-call rejection.

Cross-organization record access.

Expired Passport rejection.

Expired approval rejection.

Approval replay rejection.

Parameter mutation after approval.

Telegram callback spoofing.

Sensitive-data leakage through errors/logs/UI.

Real-side-effect prevention.

Deployment
Local
text
Frontend → local FastAPI → SQLite → seeded fixtures
                         ├─ mock LLM
                         └─ mock Telegram
Staging
text
Hosted frontend → HTTPS FastAPI → PostgreSQL-compatible DB
                                  ├─ Telegram bot
                                  └─ optional LLM provider
Use separate credentials and synthetic data for staging.

Retention and Reset
V1 synthetic records remain until an explicit owner-confirmed reset.

Reset must:

Require confirmation.

Delete Attack Lab simulation records first.

Delete dependent demo workflow records in FK-safe order.

Preserve or recreate the seeded owner and organization.

Record a reset marker.

Never affect production data.

Never delete immutable audit history outside synthetic demo reset policy.

Production retention duration is unresolved and must be decided before production use.

Technical Risks
LLM Passport output may be invalid or over-permissive.

Telegram credentials may be unavailable.

Polling may become inefficient at larger scale.

SQLite concurrency differs from PostgreSQL.

Context-aware detection may create false positives.

A tool adapter may accidentally bypass the gateway.

Safe restart could be misunderstood as resuming the quarantined session.

Missing audit events could weaken explainability.

Demo reset could delete records unexpectedly if not isolated.

Final Technical Decisions
The V1 technical baseline is:

Modular monolith.

React frontend.

FastAPI backend.

SQLite locally.

PostgreSQL-compatible staging.

Polling rather than SSE.

Deterministic Passport compiler fallback.

Mock tools only.

One seeded owner/admin.

Organization-scoped authorization.

Backend enforcement gateway.

Context-aware deterministic policy.

Telegram as optional adapter.

Append-only audit events.

Simulation-only Attack Lab baseline.

New restricted Passport/session for safe restart.