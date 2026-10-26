# Local enquiry workflow preview

This is an opt-in local prototype, not the hosted enquiry pipeline. All enquiries, reply confirmations and tasks stay in the current browser tab. Refresh, reset, end or 30-minute expiry discards them. Switching between the customer and staff views preserves them without extending expiry. No new database tables, public submission endpoint or email service have been added.

## Open and test

1. Open http://127.0.0.1:8810/#/login and choose **Try staff demo**. If an older demo is already running, open the link in a new tab so its temporary edits are preserved.
2. Choose **Switch to customer website view**. Open a vehicle if desired, then complete the enquiry form with Alex Morgan, alex@example.com and “Can I view the Ford Puma on Saturday?” The source is fixed to Website. Choose **Submit website enquiry**. Confirm that the receipt shows the actual enquiry number.
3. Choose **Switch to staff view**. The same enquiry appears in the queue with source Website, customer details, linked vehicle, New status and received activity.
4. Enter a reply subject and message. **Open in email app** creates a mailto draft in the device's configured email application; it does not automatically send, record or verify an email. The enquiry remains New. For a real send test, use your own email address when creating the enquiry. Do not send mail to the example address.
5. After sending, return and check **I sent this email**, then choose **Record sent email**. For a simulation only, manually confirming exercises the same temporary transition but must not be represented as a delivered message. The activity says Email marked as sent, with the staff-demo identity, timestamp and entered reply. The enquiry becomes Contacted. The email app may change the draft; this prototype cannot read those changes or verify delivery.
6. Choose **Schedule follow-up**. The enquiry is preselected. Set a date and “Check availability and confirm Saturday viewing time”, then save. Return to Enquiries or Overview to see the next action.
7. Try closing with a written outcome while that task is still open: the prototype rejects closure and keeps the enquiry open. Complete the task in Follow-ups, return to the enquiry and close it with an outcome such as “Viewing confirmed; no further action needed”. Confirm Closed and the closing activity. Completing the task alone does not close the enquiry.
8. Under **Record enquiry**, select Phone, Email, WhatsApp, SMS, Walk-in, Website or Other and enter another conversation. These are source labels only; there are no messaging integrations. Filter the staff queue by source to find it.
9. Reset the demo to clear the enquiries, replies and tasks. A new demo starts with the current public vehicle/photo snapshot.

## Rebuild this local preview

With the existing dependencies installed, build the frontend from the repository root in PowerShell:

```powershell
$env:VITE_ENQUIRY_DEMO='true'
npm --prefix frontend run build
Remove-Item Env:VITE_ENQUIRY_DEMO
```

Run the existing FastAPI app on loopback port 8810 using a separately migrated local SQLite database. The browser feature also checks for localhost or 127.0.0.1. Default builds disable the prototype. No flag is added to Vercel and no hosted database is changed.

The current local preview database contains ten copies of public listing fields and their public, credited photo bytes. It contains no copied private accounts or customer records. Its filename is data/login-preview-20261026.sqlite3 and it remains ignored by Git.

Tests are in frontend/src/DemoEnquiries.test.tsx. Browser-only demo actions pass through the central API client's existing in-memory interception. Their /api/demo paths are not server endpoints and cannot be used as a production integration contract.
