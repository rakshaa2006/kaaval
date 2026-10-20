Architecture Summary
Kaaval is a modular monolith that places a backend enforcement gateway between an AI agent and protected tools.

text
┌─────────────────────────────────────────────────────────┐
│                    React Web Application                  │
│  Dashboard · Tasks · Sessions · Incidents · Audit Lab    │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS JSON API
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
│                                                         │
│  Authentication · Authorization · Task API               │
│  Passport Compiler · Session API · Audit API              │
│  Approval API · Incident API · Attack Lab API             │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    Application Services                  │
│                                                         │
│  Enforcement Gateway                                    │
│  Context-Aware Data Inspector                            │
│  Mock Tool Registry                                      │
│  Kaaval Sentinel                                        │
│  Approval Service                                        │
│  Notification Service                                    │
│  Audit Service                                           │
└───────────────┬─────────────────────┬───────────────────┘
                │                     │
                ▼                     ▼
┌──────────────────────────┐  ┌───────────────────────────┐
│ Relational Database      │  │ External Adapters         │
│ SQLite local             │  │ Telegram                  │
│ PostgreSQL staging       │  │ Optional LLM              │
│ Synthetic fixtures       │  │ Mock adapters             │
└──────────────────────────┘  └───────────────────────────┘
The agent can propose an action, but it cannot execute a protected tool directly. Every tool call must pass through the enforcement gateway, which applies the active Task Passport, contextual privacy rules, approval requirements, and fail-closed behavior.

The architecture follows least-privilege and least-agency principles: an agent receives only the tools and authority needed for its task and duration.

Architectural Goals
The architecture must:

Enforce task-scoped permissions.

Keep authorization on the backend.

Prevent direct frontend-to-tool access.

Prevent real external side effects.

Fail closed when a required safety decision cannot be completed.

Support synthetic local demos without external credentials.

Provide persistent action, decision, incident, and audit records.

Keep quarantined sessions from resuming.

Support a future PostgreSQL deployment without changing the domain model.

Allow optional LLM and Telegram integrations without making them mandatory for local operation.

Non-Goals
V1 does not require:

Microservices.

Kubernetes.

Distributed agent workers.

Real email delivery.

Real backup deletion.

User-uploaded documents.

Multiple active user roles.

Production-grade multi-tenancy.

WebSocket or SSE streaming.

Autonomous incident resolution.

Fully automated policy learning.

Production compliance certification.

Architectural Style
Modular Monolith
Use one backend deployment containing clearly separated modules:

text
backend/
  app/
    main.py
    config.py
    api/
    auth/
    models/
    schemas/
    repositories/
    services/
    policy/
    tools/
    integrations/
    attack_lab/
    audit/
    db/
A modular monolith is appropriate for V1 because:

The product is a tightly coupled safety workflow.

Transactions span actions, decisions, quarantine, incidents, notifications, and audit events.

One deployment simplifies the hackathon demo.

The module boundaries preserve a path to later service extraction.

Local development remains simple.

Do not split the enforcement gateway, Sentinel, and audit service into separate network services during V1.

Trust Boundaries
Boundary 1: Browser to API
The browser is an untrusted client.

The backend must not trust:

Organization IDs from the browser.

User role values from the browser.

Client-side permission results.

Client-side session status.

Approval flags.

Tool-execution results.

Hidden form fields.

The backend derives identity and organization scope from the authenticated browser session.

Boundary 2: Agent to Enforcement Gateway
The agent is allowed to propose actions but is not trusted to authorize them.

The agent cannot:

Expand its Passport.

Choose the final policy decision.

Approve its own action.

Bypass the gateway.

Resume a quarantined session.

Modify audit events.

Boundary 3: Source Document to Agent
Source documents are untrusted input.

An invoice may contain instructions that attempt to:

Change the task.

Ignore the Passport.

Request external data transmission.

Request destructive operations.

Impersonate an owner or system message.

Document instructions cannot expand permissions.

Boundary 4: Backend to Mock Tools
Mock tools are server-side adapters. They must reject calls that do not contain a server-generated authorization context from the enforcement gateway.

Boundary 5: Backend to Telegram
Telegram is an external notification and approval channel.

The backend must:

Validate the configured webhook secret.

Validate the Telegram chat ID.

Validate approval ID and expiry.

Protect against replay.

Never include full sensitive values.

Never treat Telegram delivery as authorization.

Telegram supports a webhook secret_token, sent in the X-Telegram-Bot-Api-Secret-Token header, which should be validated by the webhook endpoint.

System Components
Frontend Application
The frontend provides:

Login.

Dashboard.

Create Task.

Passport Review.

Task Details.

Session Monitor.

Approval Preview.

Incident List.

Incident Details.

Safe Restart Review.

Audit Timeline.

Attack Lab.

Settings.

The frontend uses JSON APIs and polling in V1.

The frontend must not:

Call tools directly.

Call Telegram directly.

Call the LLM directly.

Decide whether an action is safe.

Persist security-critical state only in browser storage.

API Layer
The API layer is responsible for:

Authentication.

Request validation.

Authorization dependencies.

Organization scoping.

Response serialization.

Error mapping.

Request IDs.

Calling application services.

API route handlers should remain thin. Business rules belong in services.

Authentication Module
Responsibilities:

Login.

Demo login in synthetic mode.

Browser-session creation.

Browser-session validation.

Session revocation.

Current-user lookup.

Authentication audit events.

Task Module
Responsibilities:

Task creation.

Task retrieval.

Task cancellation.

Task status transitions.

Task audit events.

Passport Module
Responsibilities:

Deterministic Passport compilation.

Optional LLM adapter.

Structured output validation.

Tool-registry validation.

Passport versioning.

Passport activation.

Passport expiration.

Restricted restart Passport creation.

Enforcement Gateway
The Enforcement Gateway is the primary security boundary.

Responsibilities:

Validate session.

Validate active Passport.

Validate tool.

Validate arguments.

Inspect source and destination.

Detect sensitive findings.

Apply policy.

Persist decisions.

Require approval where appropriate.

Quarantine severe actions.

Invoke mock tools only after authorization.

Persist execution result.

No protected mock tool may be invoked outside this service.

Context-Aware Data Inspector
Responsibilities:

Inspect source document context.

Identify sensitive-data findings.

Identify prompt-injection indicators.

Produce masked findings.

Provide recommended policy signals.

Never make the final authorization decision alone.

V1 finding categories:

text
CUSTOMER_EMAIL
PHONE_NUMBER
GOVERNMENT_ID_LIKE
CUSTOMER_LIST
PROMPT_INJECTION
Tool Registry
The Tool Registry is the canonical list of available tools.

Each tool definition includes:

Tool name.

Read/write/destructive classification.

Argument schema.

Required context.

Side-effect classification.

Supported destinations.

Required Passport permission.

Mock executor.

V1 tools:

text
read_invoice
send_email
delete_backup
Mock Tool Adapters
Invoice reader
Reads local synthetic fixtures.

Email adapter
Records a simulated email attempt and returns a mock result. It never sends email.

Backup adapter
Records a simulated deletion attempt and returns a mock result. It never deletes a real backup or file.

Approval Module
Responsibilities:

Create approval requests.

Display masked summaries.

Enforce expiry.

Resolve approval or denial.

Prevent replay.

Bind approval to exact action arguments and destination.

Create approval audit events.

Trigger notification delivery.

An approval must be specific to the current actor, exact action, and valid time window. A client-side confirmation flag is insufficient.

Sentinel Module
Responsibilities:

Classify severe policy outcomes.

Quarantine sessions.

Create incidents.

Create notification intents.

Record containment audit events.

Prevent further execution.

Sentinel cannot:

Grant permissions.

Resume sessions.

Approve actions.

Delete records.

Modify an active Passport.

Notification Module
Responsibilities:

Send Telegram notifications.

Send mock notifications.

Persist notification status.

Retry failed notifications.

Validate webhook callbacks.

Avoid sensitive-data leakage.

Notification delivery failure must never result in session resumption or action execution.

Audit Module
Responsibilities:

Append audit events.

Mask metadata.

Query chronological events.

Filter by organization, task, session, incident, event type, decision, and simulation flag.

Prevent normal update/delete operations.

Attack Lab Module
Responsibilities:

Store predefined cases.

Simulate unsafe baseline behaviour.

Invoke the real enforcement gateway for protected behaviour.

Store baseline and protected results.

Mark all simulation events.

Reset synthetic simulation data.

The baseline must never invoke an unprotected real tool.

Request Lifecycle
Safe allowed action
text
Agent proposes read_invoice
        ↓
API validates authenticated context
        ↓
Session and Passport are validated
        ↓
Source document and task context inspected
        ↓
Policy returns ALLOW
        ↓
Action, decision, and audit records committed
        ↓
Mock invoice reader executes
        ↓
Execution result and audit event committed
        ↓
Frontend displays allowed action
Blocked action
text
Agent proposes send_email
        ↓
Gateway validates session and Passport
        ↓
Context inspector detects restricted destination/data
        ↓
Policy returns BLOCK
        ↓
Action, findings, decision, and audit records committed
        ↓
Mock email tool is not called
        ↓
Frontend displays blocked result
Approval-required action
text
Agent proposes legitimate supplier reminder
        ↓
Gateway evaluates action
        ↓
Policy returns REQUIRES_APPROVAL
        ↓
Action, approval request, notification, and audit records committed
        ↓
Owner resolves approval
        ↓
Approval is checked and consumed atomically
        ↓
Exact mock email action executes
        ↓
Execution and audit records are written
Quarantine action
text
Agent proposes severe unsafe action
        ↓
Gateway evaluates action
        ↓
Action and finding records are created
        ↓
Policy returns BLOCK with severe risk
        ↓
Session is changed to QUARANTINED
        ↓
Incident is created
        ↓
Notification intent is created
        ↓
Audit events are committed
        ↓
No later session action can execute
Safe restart
text
Owner reviews contained incident
        ↓
Owner confirms restricted permissions
        ↓
New RESTRICTED_RESTART Passport is created
        ↓
New session is created
        ↓
Original session remains QUARANTINED
        ↓
New session permits only local safe work
Data Architecture
Primary database
Use a relational database because the domain contains:

Strong ownership relationships.

Versioned Passports.

State transitions.

One-to-one policy decisions.

Approval uniqueness.

Incident references.

Append-only audit relationships.

Transaction boundaries.

Local development may use SQLite. Staging should use PostgreSQL-compatible storage. SQLAlchemy-compatible database layers support both SQLite and PostgreSQL deployments.

Core entities
text
organizations
users
auth_sessions
tasks
task_passports
source_documents
agent_sessions
action_requests
policy_decisions
data_findings
approval_requests
notifications
incidents
audit_events
attack_runs
attack_cases
Important relationships
text
Organization
 ├── Users
 ├── Tasks
 ├── Source Documents
 ├── Incidents
 ├── Notifications
 └── Audit Events

Task
 ├── Task Passports
 ├── Agent Sessions
 └── Action Requests

Passport
 └── Agent Sessions

Agent Session
 ├── Action Requests
 └── Incidents

Action Request
 ├── Policy Decision
 ├── Data Findings
 ├── Approval Request
 └── Incident trigger

Incident
 └── Notifications

Attack Run
 └── Attack Cases
State Architecture
Task state
text
PASSPORT_GENERATING
PASSPORT_GENERATION_FAILED
PASSPORT_REVIEW
ACTIVE
RUNNING
COMPLETED
EXPIRED
CANCELLED
Passport state
Generation:

text
GENERATED
FAILED
INVALID
Activation:

text
DRAFT
ACTIVE
SUPERSEDED
EXPIRED
CANCELLED
Session state
text
STARTING
ACTIVE
WAITING_APPROVAL
COMPLETED
FAILED
EXPIRED
QUARANTINED
No transition may move QUARANTINED to ACTIVE.

Action decision
text
ALLOW
REQUIRES_APPROVAL
BLOCK
BLOCKED_FAIL_CLOSED
Incident state
Containment:

text
PENDING
CONTAINED
FAILED
Owner review:

text
OPEN
REVIEWED
RESOLVED
Recovery:

text
NOT_STARTED
RESTRICTED_RESTART_CREATED
NOT_AVAILABLE
Notification state
text
PENDING
SENT
FAILED
RETRYING
Approval state
text
PENDING
APPROVED
DENIED
EXPIRED
FAILED
API Architecture
API conventions
Prefix all application endpoints with /api.

Use JSON requests and responses.

Use UUID identifiers.

Return the standard error envelope.

Include a request ID in responses and logs.

Validate all input with Pydantic schemas.

Avoid exposing ORM objects directly.

Scope all repository calls by organization.

Endpoint groups
Health
text
GET /api/health
GET /api/ready
Authentication
text
POST /api/auth/login
POST /api/auth/demo-login
POST /api/auth/logout
GET /api/auth/me
The demo-login endpoint must reject non-synthetic environments.

Tasks and Passports
text
POST /api/tasks
GET /api/tasks/{task_id}
POST /api/tasks/{task_id}/passport/generate
GET /api/tasks/{task_id}/passport
POST /api/tasks/{task_id}/passport/activate
POST /api/tasks/{task_id}/passport/regenerate
POST /api/tasks/{task_id}/cancel
Sessions and actions
text
POST /api/tasks/{task_id}/sessions
GET /api/sessions/{session_id}
GET /api/sessions/{session_id}/timeline
POST /api/sessions/{session_id}/actions
POST /api/sessions/{session_id}/quarantine
Approvals
text
GET /api/approvals
POST /api/approvals/{approval_id}/resolve
POST /api/approvals/{approval_id}/retry-notification
Incidents
text
GET /api/incidents
GET /api/incidents/{incident_id}
POST /api/incidents/{incident_id}/retry-notification
POST /api/incidents/{incident_id}/safe-restart
Audit
text
GET /api/audit
GET /api/audit/{event_id}
Dashboard
text
GET /api/dashboard
Attack Lab
text
GET /api/attack-lab/cases
POST /api/attack-lab/runs
GET /api/attack-lab/runs/{run_id}
POST /api/attack-lab/reset
Telegram
text
POST /api/integrations/telegram/webhook
Error Architecture
All API errors use:

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
Do not expose:

Tracebacks.

Database URLs.

Access tokens.

Bot tokens.

Password hashes.

Full sensitive values.

Raw prompt or invoice content.

Real-Time Update Architecture
V1 uses polling.

Polling rules
Poll active Session Monitor every 2–5 seconds.

Poll dashboard data during active operations.

Stop frequent polling after completion, failure, expiry, or quarantine.

Poll notification status when retrying.

Use server timestamps and event IDs.

On reconnection, fetch current server state rather than applying untrusted client deltas.

SSE or WebSockets may be added later behind the same query and event contracts.

Authentication and Authorization Architecture
Authentication middleware
Each protected request:

Reads the session cookie or bearer token.

Hashes and looks up the session.

Checks revocation and expiry.

Loads the active user.

Checks user activity.

Loads organization context.

Attaches authenticated context to the request.

Authorization dependency
Services must require:

text
AuthenticatedUser
OrganizationContext
Do not allow service methods to infer access from arbitrary client-supplied IDs.

Role policy
V1:

text
OWNER_ADMIN:
  read/write all synthetic organization records
  approve own organization’s approval requests
  start restricted restart
  run/reset Attack Lab
No other role has active permissions in V1.

Transaction Architecture
Task creation
Atomic unit:

Create task.

Create audit event.

Passport activation
Atomic unit:

Validate Passport.

Lock task and Passport.

Supersede any previous active Passport if applicable.

Activate selected Passport.

Update task state.

Create audit event.

Action evaluation
Atomic unit:

Create action request.

Create findings.

Create policy decision.

Create action audit event.

Create quarantine/incident if severe.

Create notification intent if needed.

The mock tool should execute only after the decision transaction commits.

Approval resolution
Atomic unit:

Lock approval.

Confirm pending status.

Check expiry.

Verify actor.

Verify exact action binding.

Mark approval resolved.

Create audit event.

The exact approved mock action executes only after successful resolution.

Safe restart
Atomic unit:

Confirm incident and original session.

Confirm original session is quarantined.

Create restricted Passport.

Create new session.

Link new session to original session.

Update incident recovery status.

Create audit events.

Notification Architecture
Adapter interface
All notification providers implement an interface equivalent to:

text
send_incident_alert(notification) -> delivery_result
send_approval_request(notification) -> delivery_result
validate_callback(request) -> callback_result
Implementations:

MockNotificationAdapter.

TelegramNotificationAdapter.

Telegram controls
HTTPS only.

Secret webhook token.

Validated owner chat ID.

Masked action summaries.

Approval ID and expiry.

Replay prevention.

Audit of received callback and resolution.

Telegram Bot API requests use the bot token over HTTPS and support configured webhook secret data for request validation.

File and Fixture Architecture
Fixture directory
text
fixtures/
  invoices/
    supplier-invoice-clean.json
    supplier-invoice-poisoned.json
Source record
Each fixture has a database record containing:

Fixture key.

Display name.

Content hash.

Trust level.

Synthetic flag.

Organization.

No upload route or file-storage bucket is required for V1.

Audit Architecture
Audit writer
All security-relevant services use one audit writer. Feature code must not construct inconsistent audit records independently.

Event requirements
Each event includes:

Organization.

Actor type.

Optional actor ID.

Event type.

Related entity IDs.

Decision.

Reason code.

Masked metadata.

Simulation flag.

Timestamp.

Append-only policy
Normal APIs cannot update or delete audit events.

Synthetic demo reset may remove demo records only through a protected reset service and must not be available outside the approved synthetic environment.

Attack Lab Architecture
Baseline
Baseline is a deterministic simulation of an unsafe agent’s attempted behaviour.

It does not:

Call real tools.

Send real messages.

Delete files.

Bypass Kaaval in execution.

Protected run
Protected runs pass the same action cases through the enforcement gateway used by the live flow.

Results
Each case stores:

Expected outcome.

Baseline simulated result.

Protected result.

Decision.

Side-effect flag.

Simulation marker.

Execution time.

Deployment Architecture
Local
text
Browser
  ↓
Vite development server
  ↓
FastAPI local server
  ↓
SQLite database
  ↓
Local fixtures
Use mock LLM and mock Telegram by default.

Staging
text
Browser
  ↓ HTTPS
Hosted frontend
  ↓ HTTPS
FastAPI service
  ↓
PostgreSQL-compatible database
  ├── Telegram adapter
  └── optional LLM adapter
Configuration
Use environment variables or a secret manager for:

Database URL.

Session secret.

Password seed configuration.

Telegram bot token.

Telegram webhook secret.

LLM API key.

CORS origins.

Environment name.

Never expose secrets in the frontend bundle.

Observability
Request logging
Log:

Request ID.

Method and route.

Organization ID where safe.

User ID where safe.

Status code.

Latency.

Error code.

Security metrics
Track:

Actions evaluated.

Actions allowed.

Actions requiring approval.

Actions blocked.

Fail-closed decisions.

Quarantined sessions.

Incidents created.

Notification failures.

Approval expiry/replay attempts.

Attack Lab runs.

Do not log full sensitive values.

Testing Architecture
Unit tests
State transitions.

Passport compiler and validator.

Tool registry.

Context inspector.

Policy evaluator.

Masking.

Error mapping.

Notification adapters.

Attack Lab definitions.

Integration tests
Authentication.

Organization scope.

Task and Passport lifecycle.

Action enforcement.

Approval transaction.

Quarantine and incident creation.

Safe restart.

Audit events.

Telegram webhook validation.

End-to-end tests
The primary browser test must cover:

Login.

Create task.

Generate Passport.

Review and activate.

Start session.

Allow invoice read.

Block unauthorized email.

Block deletion.

Quarantine session.

Review incident.

Keep old session quarantined.

Create restricted restart.

Complete restricted work.

Review audit timeline.

Run Attack Lab.

Security tests
Direct tool invocation is rejected.

Cross-organization records are inaccessible.

Expired Passports cannot authorize actions.

Expired approvals cannot execute.

Approval replay is rejected.

Action mutation invalidates approval.

Telegram callback spoofing is rejected.

Sensitive data does not leak through UI, logs, or errors.

Mock tools have no real side effects.

Scalability Path
V1 remains a modular monolith.

Future extraction candidates:

Notification worker.

Attack Lab worker.

LLM Passport compiler.

Policy evaluation service.

Audit event pipeline.

The database model should remain the source of truth for:

Task state.

Passport state.

Session state.

Action decisions.

Approval state.

Incident state.

Do not introduce asynchronous distributed processing until the synchronous transaction boundaries are proven.

Architecture Risks
LLM over-permissioning
Mitigation:

Deterministic compiler fallback.

Structured validation.

Tool registry allowlist.

Human Passport activation.

LLM cannot make final authorization decisions.

Gateway bypass
Mitigation:

Keep mock tools private to the backend.

Require gateway-issued execution context.

Add direct-call rejection tests.

Avoid exposing tool adapters as public routes.

Notification spoofing
Mitigation:

Telegram secret webhook token.

Chat ID verification.

Approval expiry.

Exact action binding.

Replay protection.

State inconsistency
Mitigation:

Server-authoritative state.

Transactional updates.

Row locks where supported.

Idempotency keys for action and approval mutations.

Refresh-based recovery.

SQLite/PostgreSQL differences
Mitigation:

Enable SQLite foreign keys.

Use compatible migrations.

Run integration tests against both where practical.

Avoid relying on database-specific behaviour for security rules.

Sensitive-data leakage
Mitigation:

Mask before persistence.

Mask before logging.

Mask before notification.

Keep raw fixtures local and synthetic.

Add automated leakage tests.

Architecture Acceptance Criteria
The architecture is accepted when:

The repository’s existing stack has been inspected.

The frontend cannot call protected tools directly.

All tool calls pass through the enforcement gateway.

Passport permissions are task-scoped and time-limited.

Policy evaluation fails closed.

Approval is exact, single-use, and auditable.

Quarantine prevents further execution.

Safe restart creates a new restricted session.

Original quarantined sessions never resume.

Notifications cannot approve or resume actions by themselves.

Audit events are append-only and masked.

Attack Lab baseline has no real side effects.

Local mock mode works without external credentials.

Staging can use PostgreSQL-compatible persistence.

The primary journey is covered by integration and end-to-end tests.