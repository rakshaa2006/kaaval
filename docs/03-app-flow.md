Product Flow
Kaaval lets one owner create a bounded AI task, review its permissions, start a protected agent session, observe every proposed action, respond to risky actions, contain unsafe behaviour, and review the resulting audit trail.

The application must make the following distinction clear:

The agent proposes actions.

Kaaval evaluates actions.

The mock tool executes only after authorization.

The owner may approve only actions explicitly marked REQUIRES_APPROVAL.

A quarantined session never resumes.

Navigation
Primary Navigation
The V1 sidebar or mobile navigation contains:

Dashboard

Incidents

Audit Timeline

Attack Lab

Settings

There is no standalone Tasks list or Sessions list in V1.

Tasks are accessed from:

Dashboard.

Create Task.

Task Details.

Audit Timeline.

Sessions are accessed from:

Task Details.

Incident Details.

Audit Timeline.

Route Map
Screen	Route	Entry points
Login	/login	Unauthenticated access
Dashboard	/	Login, navigation
Create Task	/tasks/new	Dashboard
Passport Loading	/tasks/:taskId/passport?state=loading	Create Task
Passport Review	/tasks/:taskId/passport	Passport Loading, Task Details
Task Details	/tasks/:taskId	Dashboard, Passport Review
Session Monitor	/sessions/:sessionId	Task Details, Incident Details
Incident List	/incidents	Navigation, Dashboard
Incident Details	/incidents/:incidentId	Incident List, Dashboard, Session Monitor
Audit Timeline	/audit	Navigation, Dashboard
Attack Lab	/attack-lab	Navigation, Dashboard
Settings	/settings	Navigation
Not Found	*	Invalid route
Approval Preview and Safe Restart Review are modal or inline states rather than standalone routes.

Actors
Owner
The owner can:

Sign in and sign out.

Create tasks.

Review and activate Passports.

Regenerate or cancel tasks during review.

Start protected sessions.

Review action decisions.

Approve or deny approval-required actions.

Review incidents.

Retry notifications.

Keep sessions quarantined.

Start safe restricted restarts.

View audit history.

Run and reset Attack Lab simulations.

Agent
The agent can:

Propose actions for a specific session.

Read only through registered mock tools.

Receive action results after Kaaval authorization.

The agent cannot:

Decide its own permissions.

Execute tools directly.

Resume a quarantined session.

Approve its own action.

Expand a Passport based on document content.

Kaaval Enforcement Gateway
The gateway:

Validates identity and scope.

Validates task/session/Passport state.

Inspects context and data findings.

Produces the final policy outcome.

Executes only authorized mock tools.

Records audit events.

Kaaval Sentinel
Sentinel:

Detects configured severe outcomes.

Quarantines sessions.

Creates incidents.

Attempts notifications.

Does not grant permissions.

Does not automatically resume sessions.

Global State Rules
Authentication
Unauthenticated users visiting protected routes are redirected to /login.

Authenticated users visiting /login are redirected to /.

Expired or revoked sessions return to /login.

Login errors remain on the Login screen.

Server authority
The server is authoritative for task, Passport, session, approval, incident, and notification state.

Refreshing the browser fetches current server state.

Client state must never reactivate a session or mark an action approved.

Organization scope
All displayed records must belong to the authenticated owner’s organization.

Synthetic environment
The application must visibly identify SYNTHETIC DEMO where relevant.

Screen Flows
S1 — Login
Purpose
Authenticate the seeded owner.

UI
Email field.

Password field.

Sign in button.

Demo login button only in synthetic mode.

Environment label.

Inline error region.

Actions
Action	Destination
Sign in success	Dashboard
Demo login success	Dashboard
Invalid credentials	Stay on Login
Expired session	Stay on Login with message
Backend unavailable	Stay on Login with retry
Forgot password	Not supported in V1
States
Initial.

Submitting.

Invalid credentials.

Inactive user.

Backend unavailable.

Successful authentication.

S2 — Dashboard
Purpose
Provide an operational overview and entry point to the primary workflow.

Content
Protection status.

Active task summary.

Active session summary.

Quarantined session summary.

Open incidents.

Recent blocked actions.

Recent audit activity.

Create Task button.

Actions
Action	Destination
Create task	Create Task
Open active task	Task Details
Open active session	Session Monitor
View incident	Incident Details
View all incidents	Incident List
View audit	Audit Timeline
Run Attack Lab	Attack Lab
Retry dashboard data	Reload Dashboard
States
Loading skeleton.

Normal populated dashboard.

No tasks.

No active sessions.

No incidents.

Recent activity empty.

Partial API failure.

Complete API failure.

Quarantined status requiring attention.

Open incidents must be visually prioritized above routine activity.

S3 — Create Task
Purpose
Capture a bounded task purpose.

UI
Task purpose textarea.

Example task.

Synthetic-data notice.

Generate Task Passport button.

Cancel button.

Example
Summarize today’s supplier invoices and flag overdue ones.

Actions
Action	Destination
Generate Task Passport success	Passport Loading
Validation failure	Stay on Create Task
Backend failure	Stay on Create Task with retry
Cancel	Dashboard
Validation
Purpose is required.

Whitespace-only purpose is invalid.

Excessively long purpose is rejected.

The task cannot be created without an owner and organization context.

S4 — Passport Loading
Purpose
Show that Kaaval is compiling and validating a temporary permission set.

UI
Task purpose.

Progress indicator.

Explanation that document instructions cannot expand permissions.

Cancel option where safe.

Actions
Action	Destination
Generation success	Passport Review
Retry	Passport Loading
Cancel	Dashboard
Generation failure	Show error and retry
States
Generating.

Slow generation.

Generation success.

Generation failure.

Invalid compiler output.

Backend unavailable.

The task remains inactive until activation.

S5 — Passport Review
Purpose
Allow the owner to inspect the generated Task Passport before activation.

Content
Task purpose.

Passport version.

Passport type.

Expiration.

Allowed tools.

Forbidden tools.

Approval-required rules.

Data constraints.

Model/provider metadata when available.

Warning that source documents cannot expand permissions.

Tool presentation
Use three explicit groups:

Allowed.

Approval required.

Forbidden.

For example:

Tool	Status	Explanation
Read invoice	Allowed	Required for local invoice summary
Send supplier reminder	Approval required	Owner review required before simulated send
Send external customer data	Forbidden	Sensitive outbound data is restricted
Delete backup	Forbidden	Destructive action is disabled
Actions
Action	Destination
Activate Passport	Task Details
Regenerate	Passport Loading
Cancel task	Dashboard
Back	Create Task or previous supported screen
States
Valid review.

Unknown tool.

Invalid rules.

Missing expiration.

Activation loading.

Activation success.

Activation failure.

Expired before activation.

An activated Passport cannot be edited in place.

S6 — Task Details
Purpose
Show the task’s current state and provide session entry.

Content
Task purpose.

Task status.

Current Passport version.

Passport expiration.

Allowed/forbidden summary.

Current session status.

Audit summary.

Start session action.

Actions
Action	Destination
Start protected session	Session Monitor
Review Passport	Passport Review
Regenerate Passport	Passport Loading
Cancel review-stage task	Dashboard
View session	Session Monitor
View audit	Audit Timeline
Start-session rules
Start is enabled only when:

Task is not cancelled.

Passport is active.

Passport is not expired.

Owner is active.

No conflicting active session exists for the same task unless explicitly supported.

States
Passport review required.

Active and ready.

Session starting.

Session active.

Task completed.

Task expired.

Task cancelled.

Passport expired.

Not found.

S7 — Session Monitor
Purpose
Show the protected agent session and every meaningful action decision.

Content
Session status.

Task purpose.

Passport summary.

Current action.

Action timeline.

Tool name.

Masked arguments.

Source document and trust level.

Sensitive-data findings.

Policy outcome.

Plain-language reason.

Notification/incident indicator where applicable.

Action outcomes
Allowed
Display:

Allowed status.

Tool name.

Reason.

Execution result.

Timestamp.

Approval required
Display:

Pending approval status.

Tool name.

Destination.

Masked content summary.

Findings.

Reason.

Expiration.

Review action.

Blocked
Display:

Blocked status.

Tool name.

Reason code.

Plain-language explanation.

No execution result.

Fail closed
Display:

Safety check unavailable or incomplete.

Blocked by default.

Retry if the operation can be safely retried.

No tool execution.

Actions
Action	Destination
Review approval-required action	Approval Preview
View incident	Incident Details
Refresh timeline	Same screen
Retry safe request	Same screen, only when backend permits
Open task	Task Details
Open audit	Audit Timeline
States
Starting.

Active.

Evaluating action.

Waiting approval.

Allowed action.

Blocked action.

Fail-closed action.

Quarantined.

Completed.

Failed.

Expired.

Connection unavailable.

Not found.

The UI must not imply that an action is safe merely because it is allowed; it should state that it was allowed under the active Passport and policy.

S8 — Approval Preview
Purpose
Give the owner enough information to make a specific approval decision.

Content
Action requested.

Tool.

Destination.

Masked data summary.

Source document.

Source trust.

Findings.

Reason approval is required.

Expiration.

Warning that approval applies only to this exact action.

Actions
Action	Destination
Approve	Resolve approval, then return to Session Monitor
Deny	Resolve denial, then return to Session Monitor
Close	Session Monitor with approval still pending
Retry notification	Same screen or notification result
Rules
Approve is disabled while submitting.

Duplicate approval is rejected.

Expired approval cannot be approved.

Mutated action arguments invalidate approval.

Telegram and dashboard resolution are single-use.

Notification failure does not execute the action.

States
Pending.

Approval submitting.

Approved and executing.

Approved and execution failed.

Denied.

Expired.

Already resolved.

Invalid callback.

Telegram unavailable.

S9 — Quarantine State
Purpose
Make containment unmistakable and prevent accidental continuation.

Content
Prominent “Session quarantined” banner.

Triggering action.

Severity.

Plain-language reason.

Containment timestamp.

Incident reference.

Notification status.

Disabled action controls.

Keep quarantined action.

Safe restart action.

Actions
Action	Destination
View incident	Incident Details
Keep quarantined	Incident Details or same read-only state
Start safe restart	Safe Restart Review
Retry notification	Notification result
Execute new action	Not available
States
Quarantine in progress.

Quarantined.

Containment failure requiring operator attention.

Notification pending.

Notification sent.

Notification failed.

Even if notification fails, the session remains quarantined.

S10 — Incident List
Purpose
Show security incidents requiring attention.

Content
Severity.

Summary.

Task.

Session.

Containment state.

Notification state.

Recovery state.

Created time.

Owner review state.

Actions
Action	Destination
Select incident	Incident Details
Filter	Same screen
Retry loading	Same screen
States
Loading.

Incidents populated.

No incidents.

Filtered empty.

Backend error.

Retry.

S11 — Incident Details
Purpose
Explain what happened, what Kaaval did, and what the owner can do next.

Content
Incident severity.

Triggering action.

Task and session.

Source document and trust.

Findings, masked.

Policy decision.

Containment checklist.

Notification attempts.

Related audit events.

Recovery state.

Actions
Action	Destination
Keep quarantined	Same incident state
Start safe restart	Safe Restart Review
Retry notification	Same screen with updated status
Open original session	Read-only Quarantine State
Open audit	Audit Timeline
Rules
Keep quarantined never changes the original session to active.

Retry notification never changes action decisions.

Safe restart creates a new restricted Passport and session.

The original session remains quarantined.

States
Open.

Contained.

Notification pending.

Notification failed.

Reviewed.

Safe restart available.

Safe restart already created.

Incident not found.

S12 — Safe Restart Review
Purpose
Obtain explicit owner confirmation before creating a restricted recovery session.

Content
Statement that the original session remains quarantined.

New Passport type: Restricted Restart.

Allowed tools.

Disabled tools.

Data restrictions.

New session explanation.

Link to original incident.

Actions
Action	Destination
Confirm safe restart	New Session Monitor
Cancel	Incident Details
View original incident	Incident Details
Rules
Confirming creates:

New restricted Passport.

New session.

Link to original session.

Audit event.

It does not reactivate, clone runtime state from, or modify the quarantined session.

States
Review.

Creating restricted Passport.

Creating session.

Success.

Failure.

Original task expired.

Restart already created.

S13 — Audit Timeline
Purpose
Provide a chronological, masked record of actions, decisions, alerts, interventions, and recovery.

Content
Timestamp.

Event type.

Actor.

Task.

Session.

Decision.

Reason.

Masked metadata.

Simulation label where applicable.

Filters
Task.

Session.

Event type.

Decision.

Severity.

Simulation/live.

Date range if supported.

Actions
Action	Destination
Apply filter	Same screen
Clear filter	Same screen
Open related task	Task Details
Open related session	Session Monitor or read-only Quarantine State
Open incident	Incident Details
Retry loading	Same screen
States
Loading.

Events populated.

No events.

Filtered empty.

Backend error.

Masked metadata.

Simulation events visibly labelled.

Audit records are read-only.

S14 — Attack Lab
Purpose
Demonstrate Kaaval’s protection behaviour using deterministic synthetic simulations.

Content
Simulation-only banner.

Available attack cases.

Baseline simulated outcome.

Protected outcome.

Result counts.

Case details.

Run timestamp.

Cases
Unauthorized external email.

Sensitive-data exposure.

Backup deletion.

Prompt injection.

Repeated unsafe actions.

Benign invoice workflow.

Actions
Action	Destination
Run attack suite	Running state, then results
View case	Case details on same screen
Reset simulation results	Confirmation dialog
Confirm reset	Empty Attack Lab
Cancel reset	Same screen
Rules
Baseline never invokes an unprotected real tool.

Protected results use the Kaaval enforcement gateway.

Simulation records are marked is_simulation = true.

Simulations must not create indistinguishable live incidents.

States
Initial empty.

Running.

Completed.

Partial failure.

Failed.

Results available.

Reset confirmation.

Reset success.

S15 — Settings
Purpose
Show environment and owner configuration without expanding V1 scope.

Content
Organization.

Owner.

Environment.

Telegram configuration status.

Version.

Sign out.

Synthetic demo reset.

Actions
Action	Destination
Sign out	Login
Reset synthetic demo	Confirmation, then Dashboard
View Telegram status	Same screen
Test notification	Demo utility only, if implemented
Manage users	Not supported in V1
Upload documents	Not supported in V1
Any demo utility must be visibly labelled and unavailable outside synthetic mode.

S16 — Not Found
Content
Short explanation.

Go to Dashboard button.

Actions
Action	Destination
Go to Dashboard	Dashboard
Notification Flow
Emergency incident notification
Incident is created in the same transaction as quarantine.

Notification record is created as PENDING.

Telegram adapter attempts delivery.

Notification becomes SENT or FAILED.

Incident remains contained in either case.

Owner may retry failed notification.

Approval notification
Approval request is created.

Notification is attempted.

Owner approves or denies from Dashboard or Telegram.

Callback is validated.

Approval is resolved once.

Only the exact approved action may execute.

Telegram inline-button callbacks are received as callback queries and should be acknowledged by the bot after validation.

State and Navigation Rules
Back navigation
Back navigation must not:

Resubmit forms.

Approve actions.

Start sessions.

Resume quarantined sessions.

Clear server state.

Refresh
Refreshing any screen reloads server state.

Special cases:

Passport generation resumes by polling its server status.

Active sessions resume as read-only monitoring of the same server session.

Quarantined sessions remain quarantined.

Pending approvals remain pending if unexpired.

Expired approvals become expired.

Direct links
A direct link to:

Expired Passport: show expired state and review option.

Quarantined session: show read-only quarantine state.

Resolved incident: show historical details.

Unknown record: show Not Found.

Unauthorized record: return FORBIDDEN or Not Found according to backend policy.

Required Global States
Every data-dependent screen must support:

Loading.

Empty.

Populated.

Validation error.

Unauthorized.

Not found.

Expired.

Backend error.

Network failure.

Retry.

Success confirmation.

Disabled action.

Mobile layout.

Keyboard focus.

Reduced-motion behaviour.

Primary Acceptance Journey
The flow is complete when a test user can:

Sign in.

Create an invoice-summary task.

Generate and review a Passport.

Activate it.

Start a session.

Observe an allowed invoice read.

Observe a legitimate approval-required action, if demonstrated.

Observe a poisoned-invoice action blocked.

Observe deletion blocked.

Observe quarantine.

Open the incident.

Confirm the original session remains quarantined.

Attempt notification retry.

Start a restricted safe restart.

Complete local invoice work in the new session.

Review the complete audit timeline.

Run Attack Lab and see simulation labels.