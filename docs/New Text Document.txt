Product
Kaaval is a safety-control system for autonomous AI agents. It helps a business owner define a bounded task, review its permissions, monitor agent actions, block harmful or unauthorized actions, protect sensitive information, quarantine unsafe sessions, and review an auditable incident timeline.

Kaaval uses default-deny tool access, scoped permissions, human approval for selected actions, and an independent enforcement layer. These controls align with established agent-security practices such as tool allowlists, least privilege, fail-safe containment, and auditable decision logging.

Problem
Autonomous agents can read business data and invoke tools with limited human intervention. A poisoned document or unexpected instruction can cause data exposure, unauthorized communication, or destructive behavior.

Kaaval places a deterministic control layer between the agent and protected tools. The agent may propose an action, but the backend decides whether that action can execute.

The system addresses the hackathon requirement for monitoring agent actions, blocking harmful or unauthorized actions, and showing actions, alerts, and interventions in an audit interface.

Target User
The V1 user is one business owner/admin operating a synthetic Mangaluru cashew-trader demonstration.

The user is non-technical and needs plain-language explanations of:

What the agent attempted.

Which policy applied.

Whether the action was allowed, blocked, or awaiting approval.

What sensitive information was detected.

Whether the session is contained.

What action the owner can take next.

Product Scope
Included in V1
Seeded owner authentication.

Synthetic supplier-invoice data.

Natural-language task creation.

Generated Task Passport review and activation.

Protected agent sessions.

Three mock tools:

read_invoice

send_email

delete_backup

Deterministic policy enforcement.

Context-aware sensitive-data inspection.

Allowed, blocked, approval-required, and fail-closed outcomes.

Kaaval Sentinel quarantine.

Incident review.

Safe restart using a new restricted Passport and session.

Telegram emergency notifications and approval callbacks when configured.

Append-only audit timeline.

Attack Lab simulations.

Local mock mode for LLM and Telegram services.

Excluded from V1
Real customer data.

Real outbound email.

Real backup deletion.

Real destructive operations.

User-uploaded files.

Multi-user administration.

Role management beyond OWNER_ADMIN.

Manual Passport policy editing.

Unrestricted autonomous agent chat.

WhatsApp, SMS, or email notifications.

Production compliance certification.

Automatic restart of quarantined sessions.

Claims of universal security or complete attack prevention.

Authentication
V1 supports one seeded owner/admin account.

Staging may use secure password authentication. A clearly labelled demo-login shortcut is allowed only in the SYNTHETIC_DEMO environment.

The system must:

Store password hashes, never plaintext passwords.

Store browser session tokens as hashes.

Expire sessions.

Revoke sessions on logout.

Reject inactive users.

Scope every authenticated request to the owner’s organization.

V1 does not include registration, password reset, user invitations, or a user-management screen.

Primary User Journey
The owner signs in.

The owner creates the task: “Summarize today’s supplier invoices and flag overdue ones.”

Kaaval generates a Task Passport.

The owner reviews and activates the Passport.

The owner starts a protected agent session.

The agent reads the synthetic invoice.

Kaaval allows the local invoice read.

A poisoned invoice instruction requests an external email and backup deletion.

Kaaval detects the suspicious context.

Kaaval blocks unsafe actions.

Kaaval quarantines the session when the configured severity threshold is reached.

Kaaval creates an incident.

Kaaval attempts a Telegram emergency alert.

The owner reviews the incident.

The owner keeps the session quarantined or starts a safe restricted restart.

The owner reviews the audit timeline.

The owner may run Attack Lab to demonstrate protected versus simulated baseline behaviour.

Task Creation
The owner creates a task by entering a non-empty natural-language purpose.

Example:

Summarize today’s supplier invoices and flag overdue ones.

The purpose is used to generate a bounded Task Passport. The owner cannot start a session until the Passport has been generated, reviewed, activated, and has not expired.

Task Passport
A Task Passport is a temporary, versioned permission set for one task.

It contains:

Task purpose.

Allowed tools.

Forbidden tools.

Data constraints.

Approval rules.

Expiration time.

Passport type.

Generation metadata.

Passport lifecycle
text
PASSPORT_GENERATING
PASSPORT_GENERATION_FAILED
PASSPORT_REVIEW
ACTIVE
EXPIRED
CANCELLED
SUPERSEDED
An activated Passport is immutable. Regeneration creates a new version rather than modifying the active version.

Passport review
The owner can review:

Purpose.

Allowed tools.

Forbidden tools.

Approval-required tools or conditions.

Sensitive-data restrictions.

Expiration.

Model/provider metadata when available.

The Passport must explicitly state that instructions inside a document cannot expand the active permissions.

V1 does not support manual editing of Passport rules.

Mock Tools
read_invoice
Reads a seeded synthetic invoice fixture.

It may be allowed when:

The active Passport allows invoice reading.

The source document is available.

The session is active.

The invoice request stays within task purpose and data constraints.

send_email
Records a simulated outbound email attempt.

It never sends a real email.

It may be REQUIRES_APPROVAL for a legitimate supplier reminder that:

Uses an allowed destination.

Contains no sensitive customer information.

Is consistent with the task purpose.

It is BLOCK when:

The destination is unauthorized.

The content contains restricted sensitive information.

The request is caused by a suspicious document instruction.

The action is outside the Passport.

delete_backup
Records a simulated deletion attempt.

It never deletes a real backup or file.

It is blocked by default in the V1 invoice workflow.

Action Outcomes
Every proposed action receives exactly one primary outcome:

ALLOW
The action complies with the active Passport and policy rules. The backend commits the decision before invoking the mock tool.

REQUIRES_APPROVAL
The action may be legitimate but requires explicit owner approval before execution.

Approval must be:

Specific to one action.

Time-limited.

Single-use.

Auditable.

Rejected after expiry.

Protected against replay.

BLOCK
The action violates a Passport, destination, data, trust, or safety rule. The mock tool does not execute.

BLOCKED_FAIL_CLOSED
Kaaval cannot complete a required safety decision. The action is denied rather than executed.

Examples include:

Policy service unavailable.

Required source context missing.

Invalid Passport.

Unknown tool.

Malformed action arguments.

Safety classifier unavailable when classification is required.

Context-Aware Privacy
Kaaval must not rely only on keyword matching.

The final decision considers:

Task purpose.

Source-document trust.

Requested tool.

Destination.

Data findings.

Passport data constraints.

Approval rules.

Suspicious or injected instructions.

The same value may receive different decisions depending on context. For example:

A customer email used for an internal invoice summary may be allowed in masked local processing.

The same customer email sent to an external destination may be blocked.

A supplier reminder with no sensitive data may require approval.

A document instruction asking the agent to ignore the Passport is treated as untrusted content.

Sensitive-Data Detector Set
V1 detects the following categories:

CUSTOMER_EMAIL

PHONE_NUMBER

GOVERNMENT_ID_LIKE

CUSTOMER_LIST

PROMPT_INJECTION

Only synthetic values are used.

Full sensitive values must not appear in:

UI screens.

Telegram messages.

Audit metadata.

Application logs.

Error responses.

Attack Lab summaries.

Use masked representations such as:

text
r***@example.test
XXXXXX1234
Each finding should include a category, masked value, confidence where applicable, source context, and recommended policy action.

Protected Agent Sessions
A protected session is one execution of a task using one active Passport.

A session can be:

text
STARTING
ACTIVE
WAITING_APPROVAL
COMPLETED
FAILED
EXPIRED
QUARANTINED
A session must reference:

One organization.

One task.

One Passport.

One initiating owner.

A session cannot execute actions when:

It is quarantined.

Its Passport is expired.

Its Passport is cancelled or superseded.

The task is cancelled.

The owner is inactive.

The safety decision cannot be completed.

Kaaval Sentinel
Kaaval Sentinel is the containment response that reacts to severe unsafe behaviour.

Sentinel may:

Mark the session quarantined.

Stop further protected actions.

Create an incident.

Record the triggering action.

Attempt emergency notification.

Present recovery choices to the owner.

Sentinel does not independently grant permissions, resume a session, or delete data.

Quarantine
A severe unsafe action changes the current session to QUARANTINED.

The quarantined session:

Cannot execute new actions.

Cannot return to ACTIVE.

Remains linked to the incident.

Remains available for read-only investigation.

Is not automatically restarted.

Incident resolution does not change the original session status.

Safe Restart
Safe restart does not resume the quarantined session.

It creates:

A new immutable RESTRICTED_RESTART Passport.

A new agent session.

A link to the original session and incident.

The restricted Passport allows only the minimum approved local work, such as:

Reading the seeded invoice.

Producing a local summary.

Flagging overdue items.

It keeps the following disabled:

External email.

Backup deletion.

Unapproved destinations.

Any action requiring broader data access.

The owner must see and confirm these restrictions before the new session starts.

Approval Flow
A reachable V1 approval scenario is a supplier reminder email with:

An allowed destination.

No sensitive customer information.

A purpose consistent with the active task.

No destructive operation.

The owner sees:

Requested tool.

Destination.

Masked content summary.

Detected findings.

Policy reason.

Expiration.

Approve and Deny actions.

If the owner approves, the backend commits the approval and executes only the associated mock action. If the owner denies or the request expires, the tool does not execute.

Telegram may deliver the approval request and receive a validated callback when configured. Dashboard approval remains the canonical fallback.

Notifications
Kaaval may send:

Emergency incident alerts.

Approval requests.

Notification retry results.

Notification delivery is best-effort and auditable.

A failed Telegram notification must not:

Resume a quarantined session.

Approve an action.

Execute a pending action.

Mark the incident as safely handled.

The UI must show notification status and provide a retry action where supported.

Audit Timeline
Kaaval records an append-only audit timeline for:

Login and logout.

Task creation.

Passport generation.

Passport activation.

Passport regeneration.

Session creation.

Action receipt.

Data findings.

Policy decisions.

Tool execution.

Approval creation and resolution.

Quarantine.

Incident creation.

Notification attempts.

Safe restart.

Attack Lab simulations.

Demo reset.

At minimum, an action lifecycle should produce:

text
ACTION_RECEIVED
ACTION_EVALUATING
FINDING_CREATED, if applicable
ACTION_ALLOWED / ACTION_BLOCKED / ACTION_APPROVAL_REQUIRED
TOOL_EXECUTED, if applicable
APPROVAL_CREATED, if applicable
APPROVAL_RESOLVED, if applicable
SESSION_QUARANTINED, if applicable
INCIDENT_CREATED, if applicable
NOTIFICATION_SENT / NOTIFICATION_FAILED, if applicable
The timeline must show plain-language reasons and masked metadata.

Attack Lab
Attack Lab demonstrates Kaaval’s behaviour using synthetic predefined cases.

The baseline is a deterministic simulation of what an unprotected agent might attempt. No unprotected tool is executed.

The protected result passes through the real Kaaval enforcement gateway.

Attack Lab results must be labelled SIMULATION and must not appear as live incidents without that label.

The suite should include:

Unauthorized email.

Sensitive-data external exposure.

Destructive backup deletion.

Prompt injection in an invoice.

Repeated unsafe actions causing quarantine.

Benign invoice reading and summary completion.

Dashboard Requirements
The Dashboard shows:

Overall protection status.

Active task.

Active session.

Quarantined sessions.

Open incidents.

Recent blocked actions.

Recent audit activity.

Create-task action.

Links to supported incident, audit, and Attack Lab screens.

V1 does not require standalone Tasks or Sessions list pages.

Settings Requirements
Settings shows:

Organization name.

Current owner.

Environment.

Telegram configuration status.

Application version.

Sign-out.

Synthetic demo reset.

Demo-only utilities must be visibly labelled. User management, role administration, uploads, and unsupported integrations are not included.

User-Visible States
Every major screen must define:

Loading.

Empty.

Success.

Validation error.

Backend error.

Network failure.

Not found.

Expired state where relevant.

Retry action where relevant.

Disabled action state.

Critical states must be communicated by text, iconography, and layout—not colour alone.

Accessibility and Responsive Requirements
The product must support:

Keyboard navigation.

Visible focus indicators.

Semantic headings and labels.

Accessible dialogs.

Screen-reader-compatible status messages.

Minimum 44px touch targets.

Mobile-width layouts without horizontal scrolling.

Reduced-motion preferences.

Clear field-level validation.

Sufficient contrast for normal text.

Success Criteria
The V1 product is successful when:

The owner can complete the primary journey without database edits.

The allowed invoice read executes through the gateway.

Unauthorized email and backup deletion never execute.

Sensitive findings are masked.

Severe behaviour quarantines the session.

The incident contains the triggering evidence and response.

Telegram failure leaves the session safely contained.

Safe restart creates a restricted new session.

The old session never resumes.

The audit timeline explains the journey.

Attack Lab is repeatable and simulation-labelled.

The application works with mock LLM and Telegram adapters.

Risks and Assumptions
Assumptions
One organization is sufficient for V1.

One owner/admin is sufficient for the demo.

All business data is synthetic.

Mock tools are enough to demonstrate control.

Polling is sufficient for live status.

Deterministic Passport generation is available as fallback.

Telegram is optional for local development.

Risks
External LLM output may be unreliable.

Telegram credentials may be unavailable.

Context-aware detection may produce false positives.

Safe restart may appear to be a continuation unless clearly labelled.

Attack Lab baseline may be misunderstood as a real unsafe execution.

A missing audit event could weaken the product’s trust story.

A direct tool path could bypass the policy gateway if not tested.

Out-of-Scope Decisions
The following require a future product decision and are not V1 commitments:

Production retention duration.

Multi-organization support.

Additional user roles.

User invitations and password reset.

Real business-system integrations.

File-upload workflow.

Rich agent conversation interface.

Advanced model evaluation.

Compliance certification.

Automatic policy learning.

Autonomous incident resolution.