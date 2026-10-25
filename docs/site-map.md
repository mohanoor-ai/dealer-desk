# Site structure — 25 October 2026

## Customer-facing sample catalogue

- `#/home`: stencil DD identity, labelled generated flying-Roadster concept, make/price search, three featured sample selections, six compact browsing links and contact summary.
- `#/catalogue`: imported sample stock, search, make/maximum-price filters, thumbnail or list layout.
- `#/car/:id`: sample vehicle details, gallery, source/licence credits, historical reference-price explanation and contact-information link.
- `#/contact`: supplied contact information only. Currently no details supplied and no live message delivery.
- `#/privacy`: sample-data, session and browser-demo explanation.
- `#/login`: individual staff sign-in.

## Staff workspace

- `#/overview`: stock totals, enquiries and next actions.
- `#/stock`: shared saved inventory, filters, thumbnail/list layouts and Add vehicle.
- `#/vehicles/:id`: saved details, photos, status and linked enquiries; editing follows existing role/revision checks.
- `#/vehicles/new`: vehicle form.
- `#/enquiries`: staff-recorded enquiries and status changes.
- `#/follow-ups`: schedule, complete and reopen next actions.

All pages share warm white surfaces, forest green controls, stencil identity, focus states and responsive layout rules. A single footer Try demo entry reveals customer/staff simulations with their explicit memory-only explanation. Those simulations are separate from saved records.

## Data and access

`GET /api/catalogue` reads at most 100 non-archived vehicles whose model ends in `(sample)`, excluding the known `Deployment` and `Demo Motors` operational test makes. It returns only ID, make, model, year, reference price, status and credited illustrative photo metadata. No staff notes, accounts, enquiries, tasks, revisions or audit records are included. Catalogue image delivery applies the same sample/archived/illustration checks. Staff APIs and private photos still require authentication. The sample suffix acts as the explicit showcase boundary for this release; it is not a general publishing system for real stock.

Vercel Authentication remains enabled across hosted deployments. This is a customer-style interface inside the protected assessment deployment, not unrestricted public access. No website enquiry delivery, bulk uploader, mailbox, SMS or WhatsApp integration was added.

The ten imported comparison listings are samples with historical reference prices, not actual offers. The two operational test vehicles stay outside the catalogue. The Roadster hero is AI-generated concept art, not stock photography, an official product image or proof of a flying vehicle's availability. Header mark is original editable SVG.
