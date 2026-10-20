Product Experience
Kaaval is an operational safety interface for a non-technical owner. The interface must make autonomous-agent behaviour visible and explainable:

What the agent attempted.

Which tool it requested.

What data and destination were involved.

Which policy decision was made.

Why that decision was made.

Whether a tool executed.

Whether the session is contained.

What the owner can do next.

The interface should communicate control and clarity rather than fear or surveillance. It must never suggest that Kaaval guarantees complete security.

UX Principles
Explain every decision
Every action outcome must show:

Outcome.

Tool.

Reason.

Relevant policy or Passport rule.

Whether execution occurred.

Next available action.

Default deny
The UI should make the allowed tool set explicit. Forbidden tools should not look like hidden capabilities.

Containment over continuation
When a session is quarantined, the interface must make it impossible to mistake a new safe restart for resuming the old session.

Mask sensitive information
Show only masked values and safe summaries. Never show full identifiers, customer lists, raw invoice content, or untrusted prompt text when those values could expose sensitive data.

Human approval is explicit
An approval request must identify the exact action, destination, masked data, expiry, and reason. The user must understand that approval applies only to that action.

Simulation is separate
Attack Lab must look and behave differently from live operations. Simulation results must never be confused with live incidents.

Visual Direction
Use a calm operational control-room style:

Warm, light background.

Deep navy text.

Restrained teal for protected states.

Amber for review and pending approval.

Red only for blocked or critical states.

Purple for simulation.

Clear borders and hierarchy.

Minimal decorative imagery.

No cyberpunk visual language.

No flashing warnings.

No excessive gradients or glassmorphism.

The design must use more than colour to communicate status. Every status needs text, iconography, and layout distinction.

Colour Tokens
Token	Suggested value	Use
Ink 950	#102A43	Headings, navigation
Ink 800	#243B53	Body text
Ink 600	#486581	Secondary text
Paper 50	#F7F9FB	Application background
White	#FFFFFF	Cards and surfaces
Line 200	#D9E2EC	Borders and dividers
Protected	#0F766E	Allowed and active states
Protected background	#CCFBF1	Allowed surfaces
Pending	#B45309	Approval and review states
Pending background	#FEF3C7	Warning surfaces
Blocked	#B91C1C	Blocked and critical states
Blocked background	#FEE2E2	Incident surfaces
Info	#1D4ED8	Informational states
Simulation	#7E22CE	Attack Lab only
Colours must be verified against the selected text and background combinations during implementation.

Typography
Use Inter, Source Sans 3, or the existing project’s system sans-serif.

Recommended scale:

Usage	Size / line height
Display	32 / 40px
H1	28 / 36px
H2	22 / 30px
H3	18 / 26px
Body large	16 / 26px
Body	14 / 22px
Label	13 / 18px
Caption	12 / 18px
Use monospace only for:

IDs.

Event codes.

Request IDs.

Technical metadata in expandable sections.

Layout
Desktop
Maximum content width: 1280px.

Twelve-column grid where useful.

24px page gutters.

24px section spacing.

16px card padding.

8px card radius.

6px button radius.

Mobile
16px page gutters.

Single-column layout.

Navigation drawer.

Stacked cards.

Full-width primary actions.

Bottom action bars for high-priority decisions.

No horizontal scrolling.

Minimum 44px pointer target for major controls.

Navigation
Primary navigation includes:

Dashboard.

Incidents.

Audit Timeline.

Attack Lab.

Settings.

Do not add standalone Tasks or Sessions list navigation in V1. Tasks are reached through Dashboard and Task Details. Sessions are reached through Task Details, Incident Details, and the audit timeline.

Required Shared Components
App shell
Desktop sidebar.

Mobile navigation drawer.

Organization/environment indicator.

User menu.

Page title and contextual description.

Main content region.

Skip-to-content link.

Buttons
Variants:

Primary.

Secondary.

Tertiary.

Destructive.

Loading.

Disabled.

Every submitting button must:

Show a loading state.

Prevent duplicate submission.

Preserve the accessible name.

Display an error if the request fails.

Status chips
Required statuses:

Protected.

Allowed.

Pending approval.

Blocked.

Fail closed.

Quarantined.

Completed.

Expired.

Failed.

Simulation.

Status chips must include text and, where useful, an icon.

Alerts and banners
Use:

Inline validation alerts.

Informational alerts.

Warning banners.

Critical quarantine banners.

Success confirmations.

Notification delivery status.

Dialogs
Use dialogs for:

Approval Preview.

Safe Restart Review.

Attack Lab reset.

Synthetic demo reset.

Dialog requirements:

Move focus into the dialog.

Trap focus while open.

Provide a labelled title.

Provide an explicit close/cancel action.

Return focus to the triggering control.

Prevent interaction with content behind the modal.

Proper modal focus management keeps the focused control visible and prevents accidental interaction with the underlying page.

Loading states
Use:

Skeletons for dashboard cards and timelines.

Progress indicators for Passport generation.

Button-level spinners for mutations.

Textual progress status for session actions.

No indefinite animation without explanation.

Empty states
Every empty state must explain:

What is empty.

Why it is empty, if useful.

What the user can do next.

Examples:

“No protected tasks yet. Create a task to generate a Task Passport.”

“No open incidents. Kaaval has not recorded a containment event.”

“No audit events match these filters.”

Error states
Errors must:

Use plain language.

Provide an actionable next step.

Preserve entered form data where safe.

Show a retry action when appropriate.

Avoid raw stack traces and sensitive information.

Include a request ID only in expandable technical details.

Status Semantics
Allowed
Visual treatment:

Teal status chip.

Check icon.

Plain-language reason.

Execution result.

Copy example:

Allowed by the active Task Passport. The invoice was read locally.

Approval required
Visual treatment:

Amber status chip.

Clock or hand-review icon.

Clear expiry.

Review action.

Copy example:

Approval required before sending this supplier reminder.

Blocked
Visual treatment:

Red status chip.

Stop or shield icon.

Policy reason.

Explicit statement that the tool did not execute.

Copy example:

Blocked by policy. The requested destination is not allowed by this Passport.

Blocked fail closed
Visual treatment:

Red or dark-amber status.

Lock icon.

Safety-check explanation.

Retry only when safe.

Copy example:

Blocked by default because Kaaval could not complete the required safety check.

Quarantined
Visual treatment:

Persistent red banner.

Shield or containment icon.

Session status shown in the page header.

Disabled action controls.

Incident link.

Copy example:

This session is quarantined. No new agent actions can execute.

Simulation
Visual treatment:

Purple badge and border treatment.

SIMULATION label.

Clear explanation that no real external action occurred.

Screen Designs
Login
Layout
Centred authentication card.

Product name and one-sentence explanation.

Email field.

Password field.

Primary Sign in button.

Demo login only in synthetic mode.

Environment label.

Inline error region.

Copy
Sign in to review and control protected AI-agent activity.

Do not use fear-based copy such as “Stop hackers now.”

Dashboard
Layout order
Page header.

Protection status.

Open incidents.

Active task/session.

Recent blocked actions.

Recent audit activity.

Create Task action.

Protection status card
Show:

Environment.

Current protection state.

Active Passport/session count.

Quarantined session count.

Last event time.

Empty dashboard
Use a useful first action:

No protected tasks yet. Create a task to generate a scoped Task Passport.

Primary action:

Create task

Incident priority
Open incidents must appear above routine activity. The Dashboard must not bury a quarantine event below ordinary audit activity.

Create Task
Layout
Page title.

Short explanation.

Large labelled textarea.

Example task.

Synthetic-data note.

Primary Generate Task Passport button.

Secondary Cancel button.

Guidance
Describe what the agent should accomplish. Kaaval will generate a temporary permission set for your review.

Validation
Show field-level errors for:

Empty input.

Whitespace-only input.

Excessive length.

Backend validation failure.

Passport Loading
Layout
Task purpose.

“Generating Task Passport” heading.

Progress indicator.

Short explanation of validation.

Retry and Cancel controls when appropriate.

Copy
Kaaval is converting the task purpose into temporary, reviewable permissions. Document instructions cannot expand these permissions.

Passport Review
Layout
Task purpose.

Passport status and expiration.

Permission summary.

Allowed tools.

Approval-required rules.

Forbidden tools.

Data constraints.

Document-instruction warning.

Primary activation action.

Permission cards
Each tool card should display:

Tool name.

Status.

Risk level.

Plain-language reason.

Data/destination restriction.

Approval requirement where applicable.

Example
Tool	Status	UI explanation
Read invoice	Allowed	Reads the seeded invoice for local summarization
Send supplier reminder	Approval required	Owner review is required before simulated sending
External customer-data email	Forbidden	Sensitive outbound data is restricted
Delete backup	Forbidden	Destructive actions are disabled
Task Details
Layout
Task header and status.

Purpose.

Passport summary.

Expiration.

Session panel.

Start session action.

Activity summary.

State-specific actions
Passport review: Review Passport.

Active and ready: Start protected session.

Expired: Review or regenerate Passport.

Cancelled: Read-only details.

Completed: View session/audit.

Running: Open Session Monitor.

Session Monitor
Layout
Session header and status.

Current action card.

Passport summary.

Action timeline.

Findings panel.

Related incident or approval panel.

Timeline item
Each event should show:

Time.

Tool.

Outcome.

Reason.

Source.

Destination if applicable.

Masked findings.

Whether execution occurred.

Avoid
Dense raw JSON by default.

Unexplained policy codes.

Full invoice content.

Ambiguous “success” labels that hide a block or failure.

Technical metadata may be expandable.

Approval Preview
Layout
Modal or full-screen mobile sheet.

Action summary.

Tool.

Destination.

Masked data.

Findings.

Reason.

Expiry countdown or timestamp.

Approve and Deny actions.

Approval copy
This approval applies only to the action shown here. It cannot expand the Task Passport or approve future actions.

Button hierarchy
Approve: primary or amber-confirmation action.

Deny: destructive/secondary action depending on design system.

Close: tertiary.

Do not make Approve visually indistinguishable from ordinary navigation.

Quarantine State
Layout
Full-width critical banner.

“Session quarantined” heading.

Trigger summary.

Containment checklist.

Incident link.

Notification state.

Safe restart explanation.

Disabled controls
Disable:

Send action.

Resume.

Continue task.

Approve from the quarantined session.

Safe restart copy
Safe restart creates a new restricted session. It does not resume this quarantined session.

Incident List
Layout
Page header.

Severity/status filters.

Incident rows/cards.

Timestamp.

Task/session references.

Notification and recovery state.

Empty state
No open incidents. Kaaval has not recorded a containment event.

Mobile
Use stacked incident cards instead of a horizontally scrolling table.

Incident Details
Layout order
Severity and summary.

What the agent attempted.

What Kaaval detected.

What Kaaval blocked or contained.

Notification status.

Recovery actions.

Audit timeline.

Primary actions
Keep quarantined.

Start safe restart.

Retry notification.

Explanation hierarchy
Show plain-language explanation first. Put event IDs, policy versions, classifier metadata, and request IDs in expandable technical details.

Safe Restart Review
Layout
Original incident summary.

Original session status.

New restricted Passport summary.

Allowed tools.

Disabled tools.

Data restrictions.

Confirmation action.

Mandatory statement
The original session will remain quarantined. A new restricted session will be created.

Confirmation
The primary action should state the result:

Create restricted session

Avoid a vague label such as “Continue.”

Audit Timeline
Layout
Page header.

Filter controls.

Chronological event list.

Expandable details.

Simulation/live marker.

Event copy
Use human-readable labels:

Task created.

Passport activated.

Invoice read allowed.

External email blocked.

Session quarantined.

Incident notification failed.

Restricted session created.

Do not expose only internal event codes.

Attack Lab
Layout
Purple Simulation banner.

Explanation of baseline and protected runs.

Run Attack Suite button.

Case cards.

Result counts.

Protected outcome summary.

Baseline outcome summary.

Simulation copy
Attack Lab uses synthetic scenarios. The baseline is simulated; no unprotected tool is executed.

Result presentation
Clearly distinguish:

Baseline attempted behaviour.

Kaaval protected outcome.

Expected outcome.

Actual protected outcome.

Whether a real side effect occurred.

Settings
Layout
Organization.

Owner.

Environment.

Telegram status.

Application version.

Sign out.

Synthetic demo reset.

Any notification test or reset control must be labelled as a demo utility and shown only where allowed.

Responsive Behaviour
Desktop
Persistent sidebar.

Two-column detail layouts where useful.

Fixed-width action panels only when they do not obscure content.

Timeline and evidence panels may sit side by side.

Mobile
Navigation drawer.

One-column cards.

Full-width primary actions.

Approval Preview becomes a full-screen sheet.

Quarantine banner remains visible above content.

Tables become labelled stacked rows.

Long technical values wrap or collapse.

No horizontal scrolling.

Accessibility
The interface should target WCAG 2.2 AA practices.

Keyboard
All controls reachable by keyboard.

Visible focus indicators.

Logical tab order.

Escape closes dismissible dialogs.

No keyboard trap except inside an active modal dialog.

Focus returns to the triggering control after a dialog closes.

WCAG 2.2 requires keyboard-operable interfaces to provide visible focus and includes requirements for focus appearance and focus not being obscured.

Focus
Use :focus-visible or an equivalent focus style.

Recommended focus treatment:

At least 2px visible outline.

Strong contrast against both component and background.

Avoid removing browser focus styles without replacement.

Dialogs
Dialogs must:

Have an accessible name.

Move focus inside on open.

Trap focus while open.

Prevent background interaction.

Return focus on close.

Keep the focused element visible.

Status messages
Use accessible status/live regions for:

Passport generation completion.

Action outcome updates.

Quarantine event.

Approval resolution.

Notification result.

Attack Lab completion.

Status messages should be announced without unexpectedly moving focus. WAI-ARIA status and alert/live-region techniques are commonly used for this purpose.

Forms
Every field has a visible label.

Errors are connected to fields.

Required fields are identified.

Validation does not depend only on colour.

Submitted values remain after recoverable errors.

Contrast
Verify:

Normal text.

Secondary text.

Borders and controls.

Focus indicators.

Status chips.

Disabled controls where applicable.

Motion
Use subtle 150–200ms transitions for:

Dialog appearance.

Status changes.

Loading indicators.

Timeline insertion.

Do not:

Flash incident content.

Continuously pulse red controls.

Use animation as the sole status signal.

Prevent access when animation is disabled.

Respect prefers-reduced-motion.

Content Guidelines
Prefer
“Blocked by policy.”

“Approval required.”

“This session is quarantined.”

“The tool did not execute.”

“Sensitive value masked.”

“Create a new restricted session.”

Avoid
“AI failed.”

“100% secure.”

“Threat neutralized forever.”

“The agent is dangerous.”

“Approve all.”

“Continue” when the action creates a new session.

Full sensitive values.

Unexplained technical jargon.

Error Content
Use the backend error code only as secondary technical detail.

Example:

This session is quarantined and cannot execute new actions. View the incident to review what happened.

Technical detail:

text
Code: SESSION_QUARANTINED
Request ID: req_123
Loading, Empty, Error and Success Requirements
Every major screen must define:

Initial loading.

Mutation loading.

Empty state.

Validation error.

Backend error.

Network failure.

Not found.

Expired state where applicable.

Success confirmation.

Retry action.

Disabled action state.

Component Acceptance Criteria
A component is complete only when:

It has a semantic accessible name.

It supports keyboard interaction.

It has visible focus.

It has loading and disabled states where applicable.

It has error handling where applicable.

It works at mobile width.

It respects reduced motion.

It does not expose sensitive data.

It does not imply unsupported behaviour.

Design Risks
Too many cards can make the Dashboard feel repetitive and reduce hierarchy.

Red used for every blocked action can create alarm fatigue.

A safe restart can be misunderstood as resuming the old session.

Dense audit metadata can overwhelm non-technical users.

Simulation results can be mistaken for live incidents.

A disabled button without explanation can appear broken.

Polling updates can surprise keyboard or screen-reader users unless announcements are restrained.

Final UI Acceptance Journey
A test user must be able to:

Sign in.

Create an invoice-summary task.

Understand Passport generation.

Review permissions.

Activate the Passport.

Start a session.

See an allowed invoice read.

See a legitimate approval-required action when demonstrated.

See a poisoned or unauthorized action blocked.

See a session quarantined.

Understand why quarantine occurred.

Review the incident.

Keep the original session quarantined.

Confirm a restricted safe restart.

Use the new restricted session.

Review audit events.

Run Attack Lab and distinguish simulation from live activity.