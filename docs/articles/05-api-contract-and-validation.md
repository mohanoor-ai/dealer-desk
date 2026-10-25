# Keeping the browser and API in agreement

Mohammed Sheikh-Noor · 25 October 2026 · Prepared with AI assistance.

The browser and backend need a shared description of a vehicle, enquiry and follow-up. Dealer Desk retains an OpenAPI contract alongside its FastAPI implementation. The contract check compares the implemented API with the committed description.

Browser requests go through frontend/src/api.ts. That client supplies session credentials and the mutation header consistently, and turns API failures into interface errors. Components use that shared path instead of implementing their own request conventions.

Pydantic validates incoming fields before changes reach the database. A visible required field helps someone complete a form, but it cannot replace backend validation: a request can arrive without using the website form.

The distinction matters when AI tools generate both ends of a feature. Matching names on a screen are insufficient. The payload, response shape, authorization and failure behaviour must agree. Contract and API tests check those boundaries separately from interface rendering.

[OpenAPI contract](../../openapi.yaml) · [API client](../../frontend/src/api.ts) · [Contract test](../../tests/test_contract.py)

AI Dev Tools Zoomcamp project progress · [DataTalks.Club](https://datatalks.club/) · [Alexey Grigorev](https://alexeygrigorev.com/)

#aidevtools #DataTalksClub #BuildInPublic #SoftwareEngineering
