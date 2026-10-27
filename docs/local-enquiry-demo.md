> Update 27 October 2026: the demo now saves and shares test records on this browser until reset. Customer accounts and in-account conversations are available in the normal local app. See [customer continuity](customer-continuity.md) for current testing, verification-preview limits and storage behaviour. Earlier temporary-demo instructions below describe the preceding implementation.

# Local customer and staff enquiry workflow

Updated 26 October 2026. This supersedes the earlier demo-only prototype. The whole local app now supports this workflow using its database and normal staff sessions. The optional demo uses the same interface with temporary in-tab records. These changes have not been pushed, deployed or applied to Neon.

## Customer: saved local workflow

1. Open http://127.0.0.1:8810/#/catalogue and select a car.
2. Choose **Send an enquiry**. No enquiry fields appear before that button is selected. The modal shows the selected vehicle as fixed context.
3. To change the vehicle or make a general enquiry, explicitly select **Enquire about a different vehicle or make a general enquiry**. Otherwise there is no vehicle dropdown.
4. Choose availability, viewing, test drive, vehicle details, callback or Other. Enter name, email and message; callback also requires a phone number.
5. Submit. The source is assigned Website and success is shown only after the save returns the actual reference. A submission key prevents a retry from creating a second record. Keep that reference for staff review. There is no automatic email confirmation.

## Staff: saved local workflow

Sign in with an individually provisioned local staff account. Cloud staff passwords/accounts have not been copied into the local database. To create an account, use the existing interactive CLI against this exact preview database in PowerShell; enter the password privately when prompted:

```powershell
$env:DATABASE_URL='sqlite:///data/login-preview-20261026.sqlite3'
$env:APP_ENV='development'
.venv/Scripts/python.exe -m scripts.create_user local-manager --role manager
```

1. Sign in at http://127.0.0.1:8810/#/login. The dashboard shows received enquiries needing a response, contacted enquiries, pending actions, closed enquiries and overdue/today/upcoming task counts. These are existing statuses plus tasks, not invented delivery states.
2. Open Enquiries or follow the dashboard enquiry number. Review source, request, contact details, vehicle and suggested action.
3. Prepare an email reply and choose **Open in email app**. This opens a mailto draft in the device's configured mail application. It cannot send automatically, verify delivery or read changes made in the mail app. For a real send test, use your own email address when creating the enquiry; never send to the example address.
4. After sending, confirm **I sent this email**. Optionally tick **Schedule a follow-up**, edit the suggested action and set the date. **Record sent email** saves the confirmation, the entered reply, actual staff username/time and any selected task in one transaction. The enquiry becomes Contacted.
5. For calls or other conversations, use **Contact outcome** and **Record contact**. The optional follow-up checkbox works there too. Source records where the enquiry arrived; it is separate from the response method and does not connect messaging services.
6. Under **Record enquiry**, select the source and request type. Optional **Schedule a follow-up** creates the linked task atomically with the enquiry.
7. Complete the action under Follow-ups. Completing it does not close the enquiry. Close with a written outcome once no pending tasks remain. A stale revision or failed task validation must not save a partial reply or task.
8. Reload or sign in again to verify these records persist. Viewers can read the queue/activity but cannot record replies, tasks or enquiries.

## Temporary walkthrough without an account

1. Choose **Try staff demo** beneath login. It opens the dashboard.
2. Switch to customer website view, select a car and use its enquiry popup.
3. Submit, close the receipt popup, switch back to staff and follow the dashboard enquiry link.
4. Exercise reply/contact, optional follow-up and outcome/closure. These records stay in this tab and disappear on refresh, reset, end or expiry. They never write to the staff database.

A manual sent confirmation in a simulation is not proof of an actual delivered email. Automated checks exercise that transition without sending email or launching an external mail app.

## Scope, migration and verification

The ordinary frontend build now includes the workflow; no VITE_ENQUIRY_DEMO flag is required. The local server serves frontend/dist. The separately migrated preview database contains ten public listings and credited photos; it is not a copy of private production records. Backups are ignored by Git.

Migration 20261026_enquiry_workflow preserves existing record IDs and task references, adds source/request/contact/activity fields and permits a null vehicle for a general enquiry. Historical sources/requests become Other rather than being guessed. SQLite batch migration checks foreign keys and preserves status/revision constraints. Destructive downgrade is refused; use a tested backup restore if the schema must be reversed. Do not promote this migration using the previous compatible-code-rollback assumption.

Website submission returns only a reference, checks published vehicles, enforces same-origin writes and uses a bounded process-wide limiter (30 attempts per 15 minutes). It is explicitly disabled in hosted environments pending separate release approval and shared abuse-control review. Authenticated APIs retain server-side roles and revision checks. Private customer and reply text is excluded from catalogue, audit events and operational logs.

Backend checks: tests/test_enquiry_workflow.py and tests/test_workflow_migration.py. UI checks: frontend/src/DemoEnquiries.test.tsx and App.test.tsx. No external email, SMS or WhatsApp integration has been added.
