# Showing vehicles without exposing staff records

Mohammed Sheikh-Noor · 25 October 2026 · Prepared with AI assistance.

The customer website needs vehicle names, reference prices, availability and credited photographs. It does not need enquiry messages, internal notes, users or audit history. Dealer Desk uses a separate response shape for its public catalogue.

The catalogue includes a bounded selection of non-archived reference listings. Internally marked reference records can appear; known operational test makes are excluded. Photo delivery also follows the catalogue boundary instead of exposing every staff-uploaded image.

A regression test checks the public field allowlist and the exclusion of internal records and non-illustrative photos. Anonymous access to staff vehicles, enquiries and tasks still returns 401, while the public catalogue returns the ten reference listings.

The current website is a demonstration: prices are recorded reference values and photographs are illustrative. There is no connected public enquiry delivery. Keeping those statements visible prevents a browsing demonstration from looking like a live offer or a delivered customer request.

[Catalogue regression](../../tests/test_catalogue.py) · [Catalogue API](../../backend/app.py) · [Product specification](../../product-spec.md)

AI Dev Tools Zoomcamp project progress · [DataTalks.Club](https://datatalks.club/) · [Alexey Grigorev](https://alexeygrigorev.com/)

#aidevtools #DataTalksClub #BuildInPublic #SoftwareEngineering
