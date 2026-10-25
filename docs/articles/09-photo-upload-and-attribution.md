# Adding vehicle photographs with clear limits

Mohammed Sheikh-Noor · 25 October 2026

A vehicle listing needs more than one photograph, but an upload endpoint must handle files as untrusted input. Dealer Desk checks file size, decoded format and image dimensions before retaining an image.

The image processing path removes metadata and creates a thumbnail. Processed bytes and caption, source and licence fields persist with the vehicle. Staff can manage several photographs and select a cover image. Hosted storage is currently database-backed; Cloudflare R2 remains deferred.

The imported reference cars use credited illustrative photographs. The public pages show source and licence links, and screenshot documentation preserves those credits. A reference photograph must not be described as a photograph of a vehicle actually held by the dealership.

Photo tests cover validation, persistence, quotas, access and cover selection. The browser-only demo cannot upload photographs. This prevents a temporary interface demonstration from claiming an upload was saved when no persistent operation occurred.

[Photo tests](../../tests/test_photos.py) · [Photograph credits](../../sample-assets/stock/credits.json) · [Screenshot provenance](../media/README.md)

[AI Dev Tools Zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp)

#aidevtools #DataTalksClub #BuildInPublic #SoftwareEngineering
