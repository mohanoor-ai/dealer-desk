# Keeping vehicle prices in whole pennies

Mohammed Sheikh-Noor · 25 October 2026 · Prepared with AI assistance.

A vehicle price is entered in pounds, but Dealer Desk stores price_pence as an integer. For example, an input of 12.30 becomes 1230 pennies. This avoids relying on binary floating-point arithmetic for stored monetary values.

The frontend conversion rejects malformed amounts, negative values and more than two decimal places. The backend also validates incoming values. A friendly input control and a database field serve different purposes; neither should be treated as the only validation layer.

The same care applies to vehicle names. Reference listings carry an internal catalogue marker. Staff sees the ordinary model name in the editor, while the save operation preserves the existing marker without adding duplicates. Blank model names are rejected.

These details are small compared with a whole page, but they affect saved data. Tests cover exact pennies, invalid amounts and marker-preserving edits. A polished price label would not reveal a conversion error on its own.

[Frontend validation tests](../../frontend/src/App.test.tsx) · [Shared API client](../../frontend/src/api.ts)

AI Dev Tools Zoomcamp project progress · [DataTalks.Club](https://datatalks.club/) · [Alexey Grigorev](https://alexeygrigorev.com/)

#aidevtools #DataTalksClub #BuildInPublic #SoftwareEngineering
