# Trying the workflow without creating a staff account

Mohammed Sheikh-Noor · 25 October 2026

People reviewing the app need a way to explore its controls without changing shared stock. Dealer Desk has optional customer and staff demonstrations held in the current browser tab.

Demonstration operations are intercepted in JavaScript memory, with no fallback to business API writes. Refreshing, ending or resetting the demonstration discards those changes. The session expires after thirty minutes; a suspended tab may only clear its memory when it resumes.

This is not a short-lived database login. It creates no guest account, session cookie or browser-storage record. It also does not prove persistence. A screen showing a newly created demonstration enquiry is different from a saved API/database enquiry.

Photo uploads require a staff account and are unavailable in the demonstration. The visible notice explains that enquiries are not sent. Those limits make the demonstration useful without presenting temporary interactions as real dealership operations.

[Demo implementation](../../frontend/src/demo.ts) · [Architecture boundaries](../architecture.md)

[AI Dev Tools Zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp)

#aidevtools #DataTalksClub #BuildInPublic #SoftwareEngineering
