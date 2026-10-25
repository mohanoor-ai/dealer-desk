# Why staff sign-in belongs behind the public catalogue

Mohammed Sheikh-Noor · 25 October 2026 · Prepared with AI assistance.

A visitor browsing cars does not need a staff account. Editing vehicle prices, reading customer enquiries and scheduling staff work require a different boundary. Dealer Desk therefore separates public browsing from authenticated staff operations.

An operator provisions individual accounts. Passwords are stored as salted scrypt hashes. A successful login creates a random, expiring server session; the database keeps a hash of its token and the browser receives an HttpOnly cookie. Hosted HTTPS uses the Secure cookie flag.

Viewer accounts read records, sales accounts manage the workflow, and managers can inspect audit history. The backend checks those permissions. Removing an edit button from the page is useful presentation, but an unauthorized API request still needs to fail.

Logout revokes the session. Public self-registration is not implemented. Temporary demonstration access is a separate browser-memory mechanism and does not provision a staff identity. These are intentionally different ways to explore or operate the app.

[Authentication tests](../../tests/test_auth.py) · [Security boundaries](../security.md) · [Architecture](../architecture.md)

AI Dev Tools Zoomcamp project progress · [DataTalks.Club](https://datatalks.club/) · [Alexey Grigorev](https://alexeygrigorev.com/)

#aidevtools #DataTalksClub #BuildInPublic #SoftwareEngineering
