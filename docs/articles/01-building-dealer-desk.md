# Building Dealer Desk: keeping the first scope useful

Mohammed Sheikh-Noor · 25 October 2026

A dealership needs to know which vehicles are available, which enquiries need attention and what action comes next. Dealer Desk puts those records in one shared workspace. The first scope is one dealership and a staff workflow: save a vehicle, record a linked enquiry, schedule a follow-up and complete it without losing the history.

React and TypeScript provide the browser interface. One API client handles backend requests. FastAPI validates input and checks staff permissions; SQLAlchemy stores records in SQLite locally or PostgreSQL for hosted use. Alembic records schema changes. These choices are documented in the [architecture](../architecture.md), rather than being presented as mandatory course technologies.

The [specification](../../product-spec.md) separates expected behaviour from implementation status. Public issues and [acceptance criteria](../tasks.md) make changes reviewable. This matters with AI assistance: a plausible generated screen does not establish that a record was validated, saved or protected by server permissions. Those behaviours need their own checks.

The product excludes payments, vehicle-history checks and multi-dealership tenancy. The public catalogue provides browsing; live enquiry delivery and R2 storage remain deferred. Current photos persist in the database. Temporary browser demos illustrate interactions with demonstration records and disappear on reset or refresh; they are not the shared staff system.

![Actual staff overview with demonstration records](../media/dealer-overview.png)

Captured 25 October 2026 from the actual local staff interface using application code 0b1aff9 and an isolated database copy. It shows ten active reference listings, two open enquiries and no incomplete follow-ups. [Capture details and stock-photo credits](../media/README.md).

The useful boundary is a complete, small journey with clear evidence. More screens, stock records or generated descriptions do not replace persistence, permissions and reproducibility. The current [assessment index](../assessment-evidence.md) shows both evidence and remaining limits.


[AI Dev Tools Zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp)

#aidevtools #DataTalksClub #BuildInPublic #SoftwareEngineering
