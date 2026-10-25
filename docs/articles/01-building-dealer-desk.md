# Building Dealer Desk: keeping the first scope useful

Mohammed Sheikh-Noor · 25 October 2026 · Prepared with AI assistance.

A dealership needs to know which vehicles are available, which enquiries need attention and what action comes next. Dealer Desk puts those records in one shared workspace. The first scope is one dealership and a staff workflow: save a vehicle, record a linked enquiry, schedule a follow-up and complete it without losing the history.

React and TypeScript provide the browser interface. One API client handles backend requests. FastAPI validates input and checks staff permissions; SQLAlchemy stores records in SQLite locally or PostgreSQL for hosted use. Alembic records schema changes. These choices are documented in the [architecture](../architecture.md), rather than being presented as mandatory course technologies.

The [specification](../../product-spec.md) separates expected behaviour from implementation status. Public issues and [acceptance criteria](../tasks.md) make changes reviewable. This matters with AI assistance: a plausible generated screen does not establish that a record was validated, saved or protected by server permissions. Those behaviours need their own checks.

The product excludes payments, vehicle-history checks and multi-dealership tenancy. A public customer showroom and R2 storage remain separate work. Current photos persist in the database. Temporary browser demos illustrate interactions with fictional data and disappear on reset or refresh; they are not the shared staff system.

![Actual staff Overview with fictional records](../media/dealer-overview.png)

This is the real protected development app captured on 24 October from b01d342. It contains one sample vehicle, one open enquiry and no open follow-ups; the counts were not staged for the image. [Capture details and stock-photo credit](../media/README.md).

The useful boundary is a complete, small journey with clear evidence. More screens, stock records or generated descriptions do not replace persistence, permissions and reproducibility. The current [assessment index](../assessment-evidence.md) shows both evidence and remaining limits.
