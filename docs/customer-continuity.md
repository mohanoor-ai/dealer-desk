# Customer continuity and the shared saved demo

Local source update, 27 October 2026. Nothing in this change has been deployed to Vercel or applied to Neon. The submitted revision remains unchanged.

## Quick shared-demo test

1. Open http://127.0.0.1:8810/#/login and choose **Try staff demo**. It starts or resumes the saved demo dataset on this browser. The active role is per tab, while enquiries/messages/tasks are shared through this origin's local storage.
2. Switch to customer website view, open a vehicle and choose **Send an enquiry**. Enter test details and submit. The receipt shows the reference, **Back to vehicle**, **View or follow up this enquiry**, recently viewed and more vehicles. There is no Start another enquiry action. Reopening that car's form in the same tab shows its saved reference, not a fresh submission form.
3. Return to the vehicle. Switch to staff, open Enquiries and use **Reply in customer account** on that enquiry. This saves a conversation message; no email is sent.
4. Switch to customer and open **My enquiries**. Read the staff reply and add a follow-up on the same enquiry. Staff attention returns to New when a customer message arrives.
5. Refresh the page. The active demo role and conversation survive within the 30-minute session. Open a second local login tab and start staff demo to see the same records. Polling refreshes each open view about every three seconds. This is device/browser persistence, not shared cloud storage or cross-device access.
6. End demo or sign out. Its test records remain saved. Starting it again resumes them. **Reset demo** explicitly clears the saved test dataset and loads its starting catalogue snapshot; it does not delete the dealership database. Use test details only, especially on a shared device. Browser local storage can be edited/cleared by the device owner and is not an authorization mechanism for real records.

## Real local customer accounts

Open http://127.0.0.1:8810/#/account outside demo. Registration, sign in, recovery and owned enquiry conversations use a separate customer account/session system in the local SQL database. Customer credentials do not grant staff access. Staff sessions do not become customer sessions.

Registration is a local development flow: the page explicitly displays **Local email preview — no email was sent** and offers the verification/recovery link. The link expires after 30 minutes and is single use. The user must open and confirm it, then sign in. This simulates a verification email; it does not prove ownership of a real inbox. Do not use real customer data here. Hosted registration and recovery are blocked pending an actual email-delivery integration and release review.

A verified local account links previously unclaimed enquiries with the same normalized email. Authenticated website submissions must use that account's email. The customer list includes only owned enquiries, and conversation endpoints check ownership on every request. The original enquiry, customer-visible messages and status are returned; internal activity, notes, tasks, contact records and token hashes are omitted. Staff replies appear as Dealership, not as an external email-delivery claim.

A new customer follow-up uses the existing thread rather than creating another enquiry, and returns the staff attention status to New. Staff in-account messages set Contacted. Replying after closure reopens the conversation for attention without pretending the previous outcome is still final. Staff-only email confirmations and internal contact outcomes are separate from customer-visible messages.

Passwords use the existing salted scrypt helper. Customer session tokens and verification/recovery tokens are hashed in the database. Customer sessions expire after eight hours and use a separate HttpOnly/SameSite cookie (Secure under hosted HTTPS). Recovery changes the password, revokes sessions and invalidates outstanding customer tokens. Customer pages provide sign out. The current limiter is bounded and process-local; hosted public account flows require a separate deployment/abuse-control review.

## Comparison, viewed cars and policy pages

The catalogue and vehicle pages offer Compare. Up to three vehicles can be selected; comparison shows only stored photos, model names, years, prices and availability. No unknown mileage, specifications or vehicle history is invented. Compare is kept in page memory.

Recently viewed keeps up to twelve vehicle IDs in page memory by default. Optional **Remember viewed cars** persists those IDs on this device; **Essential only** does not enable that storage. Revocation/expiry clears its saved list. Choices last 180 days. The viewed list can also be cleared manually. A separate session reference ID avoids restarting a submitted enquiry from the same car. No contact details, credentials or real messages are stored in that receipt key.

Privacy, Cookies, Terms and Storage choices are linked across public, login, staff and demo pages. The policy text describes current storage/retention, local verification limits and missing trading-operator details. It does not claim a legal compliance certification or invent operator contact details. There are no advertising or analytics cookies. Starting the saved demo explicitly requests its functional browser storage, separately from optional viewed-history storage.

Expert review stars are clickable publisher model-range ratings, not customer reviews, safety ratings or individual-stock condition. Only verified source/model matches are displayed; unverified models show no stars. See [review sources](review-sources.md).

## Data and release boundary

Migration 20261026_customer_accounts adds separate customer accounts, sessions, hashed action tokens, enquiry ownership and customer-visible messages. Existing vehicle/enquiry/task IDs remain in place. Only the separate backed-up preview database has been migrated. Reverse migration requires a verified backup restore; no compatible cloud rollback across this schema is claimed.

Normal enquiries/accounts/messages persist in the SQL database. The demo intercepts business requests, persists only test snapshots in browser storage and never writes to the staff database or creates real customer accounts. Its role switch represents one shared test customer and one staff view, not real identity verification. Simultaneous writes from multiple tabs are not a transactional database guarantee; use the real local account mode for persistence/concurrency verification.

Tests: tests/test_customers.py checks account ownership, verification expiry/replay, hashing, cookie separation, recovery revocation, privacy and server roles. frontend/src/CustomerContinuity.test.tsx covers saved demo restore/role sharing/expiry/reset, receipt behaviour, storage choice, comparison limits and source-linked stars. Existing workflow/migration tests remain required.

## Compact staff actions — 27 October 2026

Each enquiry now shows a short customer/vehicle/source/status summary, the request, one pending-action line and an Action dropdown. Choose Reply in account, Reply by email, Record a call/conversation, Schedule follow-up or Close enquiry to open that form only. Reply/contact forms offer an optional Add follow-up checkbox; date/action fields appear only when selected. Account reply plus task saves atomically. Conversation, contact details and activity are collapsed under View conversation / history, with no write form in that history. Manual enquiry recording is collapsed until requested. Cancel and successful save return the selector to its compact state. Existing email confirmation, closure/permission checks and saved demo records are unchanged.

## Required fields, optional offers and leads — 27 October 2026

Website enquiry fields marked * are required: request type, name, valid email and message; a callback also requires a phone number. The vehicle remains fixed unless a different/general request is explicitly selected. Email promotions are a separate, unticked optional choice. An enquiry succeeds without marketing permission. The checkbox names Dealer Desk, the email channel and vehicle updates/offers; privacy and withdrawal links are shown separately. No marketing service or campaign sender is connected.

Explicit opt-in records the normalized email, wording/version (email-offers-v1), Website enquiry source, enquiry reference and time in a separate preference ledger. Existing records are not assumed subscribed. A later enquiry with an unticked box does not withdraw an earlier subscription; Email preferences does that explicitly. A new explicit opt-in can subscribe again after withdrawal. The latest 100 preference events are retained. This is a local record of choices, not a certification of inbox ownership or permission for a different trading operator. Actual marketing delivery would require a separately reviewed provider, operator identity and unsubscribe links.

Staff navigation now includes Leads. Enquiry contacts are grouped by normalized email; records without email remain separate rather than guessing that two people are the same. Leads show source, latest interest/request/status, contact details, number of enquiries, current email permission and the consent/withdrawal record. Open latest enquiry returns to its pipeline. Capture a lead records a staff enquiry with the source, interest and optional agreed follow-up; it cannot create marketing consent on the customer's behalf. Viewers can read, while sales/manager may capture and record withdrawal.

The global Email preferences page lets a person stop promotional email for an address without signing in or closing an enquiry/account. It returns the same generic acknowledgement for known and unknown addresses and reveals no subscription status. The local endpoint is rate-bounded and blocked in hosted environments; it only suppresses preferences and cannot subscribe or send anything. Staff can also record a requested withdrawal in Leads. The saved demo mirrors these records/preferences in its existing browser dataset, separate from actual dealership data.

Consent design was checked against the ICO's [electronic marketing guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/electronic-and-telephone-marketing/) and [electronic mail marketing rules](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-direct-marketing-using-electronic-mail/how-do-we-comply-with-the-pecr-electronic-mail-marketing-rules/). The app does not claim a legal compliance assessment. Migration 20261027_leads was applied only to the backed-up local preview database; no hosted change or campaign sending was performed.
