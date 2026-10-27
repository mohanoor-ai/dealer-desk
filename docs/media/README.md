# Screenshot provenance

Current files: dealer-overview.png and enquiry-workflow.png. Captured 25 October 2026 from the actual staff interface at loopback port 8810, with application code 0b1aff92713137a20f8007f212068c347cb4dd6d. The compiled source was unchanged between capture and that commit. The isolated SQLite copy contains demonstration records, not customer data. No credentials, session tokens or personal contact details appear.

Overview: ten active reference vehicle listings, two open enquiries (Alex Morgan and Jamie Taylor), zero incomplete follow-ups, both identified as having no next action. Operational test cars were archived, not deleted.

Collage: four unaltered browser captures composed in an HTML grid with captions, then captured as one PNG. The enquiry was saved through the staff form; the overview identified it as unscheduled; its shortcut selected enquiry #2; the linked availability-check task survived reload and was completed. The task was reopened and completed again to refresh the captures after the wording update. The enquiry remains open. No customer message, appointment confirmation or external delivery is represented.

The temporary local sales identity was signed out, disabled and its sessions revoked after capture. Raw stage captures and HTML composition remain private scratch artifacts; this PNG is the public evidence artifact. These are local saved-workflow checks, not proof of a hosted staff session or an automated mobile/browser matrix.

The older 24 October hosted Overview image from b01d342 is retained in Git history; it has been replaced here following the interface update.

## Landing page

File: landing-page.png. Captured 25 October 2026 from the actual production website at https://dealer-desk-prod.vercel.app/#/home. Public /health identified application revision 14f075b938b1cc4a3812edaea87c6d12d7b7f6b7 (version 0.4.0) at capture time. This is an unaltered browser viewport capture, not the earlier generated website mockup.

The visible header, Roadster hero, search controls and illustration notice belong to the running application. An existing staff session was present, so navigation reads Staff workspace; visitors without an app session see Staff sign in. No identity, credential, cookie or connection string appears. The hero is generated concept artwork, visibly labelled as an illustration, not a photograph of an available vehicle. Reference vehicle photos elsewhere on the page retain their own credits.

## Full-page site collage

Files: site-collage.jpg and the four originals in screenshots/. Captured 25 October 2026 from https://dealer-desk-prod.vercel.app/ after production health identified bbf5a3fbc7ace63f82fe5e4e792fb5221d9a2609. The browser used its normal desktop viewport. All photographs had loaded before catalogue capture. The full-page originals are unaltered browser captures; an HTML/CSS layout scaled them proportionally with captions into the collage. No UI content was generated or reconstructed. Browser output is JPEG, retained with matching .jpg filenames.

- [Homepage](screenshots/landing-full.jpg): /#/home, including featured vehicles, compact browsing and footer.
- [Catalogue](screenshots/catalogue-full.jpg): /#/catalogue, all ten listings.
- [Vehicle details](screenshots/vehicle-full.jpg): /#/car/3, Ford Puma with its reference-price notice and photo credit.
- [Staff overview](screenshots/staff-overview-full.jpg): /#/overview, existing authenticated manager session, ten stock vehicles and the two previously recorded demonstration enquiries for Jamie Taylor and Alex Morgan. No contact details, password or session token appears. Records were not changed for this capture.

Public browsing needs no app login. An existing staff session changes the header entry to Staff workspace. The saved staff overview is separate from the temporary browser demo and does not imply that a customer reply was sent.

## Logo

File: dealer-desk-logo.svg. Reuses the application's existing SVG emblem path and DEALER DESK wordmark, with its forest-green colour. It is a repository presentation asset, not a new brand design or a change to the owner's GitHub profile.

## Mobile navigation

Files: mobile-navigation.jpg and mobile-bottom-navigation.jpg. Actual local browser captures at 390×844 on 25 October 2026, using the compiled source committed as bbf5a3fbc7ace63f82fe5e4e792fb5221d9a2609 and the isolated loopback SQLite copy. They show the top and bottom menu controls opening the vertical customer navigation. Manual checks also covered 320×640, Escape, link selection, staff destinations and ending the browser-only demo. Viewport overrides were reset. These are local responsive checks, not an automated cross-device matrix. Production served the same compiled JavaScript/CSS bundle after release; public health matched the source revision.

## Reference photograph credits

Photographs visible in the captures are illustrative references, not actual dealership stock. Optimized/resized copies appear inside the unaltered app screenshots. The full catalogue collage contains these credited photographs:

- Ford: Vauxford; [source](https://commons.wikimedia.org/wiki/File:2020_Ford_Puma_Titanium_EcoBoost_Hybrid_1.0_Front.jpg); [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0).
- Jaecoo: © M 93; [source](https://commons.wikimedia.org/wiki/File:Jaecoo_J7_1.6T_4WD_%E2%80%93_f_21032025.jpg); [CC BY-SA 3.0 de](https://creativecommons.org/licenses/by-sa/3.0/de/deed.en).
- Kia: LuvsMG481; [source](https://commons.wikimedia.org/wiki/File:2025_Kia_Sportage_S_front_only.jpg); [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0).
- Nissan: Alexander-93; [source](https://commons.wikimedia.org/wiki/File:2024_Nissan_Qashqai_e-Power_IMG_2187.jpg); [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0).
- Vauxhall: Alexander Migl; [source](https://commons.wikimedia.org/wiki/File:Opel_Corsa-e_at_IAA_2019_IMG_0738.jpg); [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0).
- Volkswagen: Vauxford; [source](https://commons.wikimedia.org/wiki/File:2020_Volkswagen_Golf_Style_1.5_Front.jpg); [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0).
- MG: © M 93; [source](https://commons.wikimedia.org/wiki/File:MG_HS_Hybrid%2B_Luxury_(II)_%E2%80%93_f_12032026.jpg); [CC BY-SA 3.0 de](https://creativecommons.org/licenses/by-sa/3.0/de/deed.en).
- MINI: Alexander-93; [source](https://commons.wikimedia.org/wiki/File:Mini_Hatch_(J01)_Ditzingen_Mobil_IMG_9772_(cropped).jpg); [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0).
- Tesla: Alexander-93; [source](https://commons.wikimedia.org/wiki/File:Tesla_Model_3_(2023)_Autofr%C3%BChling_Ulm_IMG_9282.jpg); [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0).
- Volvo: Elise240SX; [source](https://commons.wikimedia.org/wiki/File:2019_Volvo_XC40_T5_Momentum_in_Bright_Silver_Metallic,_front_left,_2025-09-22.jpg); [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0).
- Ford: Vauxford; [source](https://commons.wikimedia.org/wiki/File:2020_Ford_Puma_Titanium_EcoBoost_Hybrid_1.0_Rear.jpg); [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0).

## Functionality diagram

File: dealer-desk-functionality.svg. Editable vector diagram prepared 25 October 2026 from the implemented public catalogue, authenticated staff workflow, API boundaries and persistence described in architecture.md. It is a functionality diagram, not a screenshot or proof of a delivered customer enquiry. It explicitly distinguishes read-only public browsing from staff-entered enquiries. The owner approved displaying it at 560px wide in README; the full-size SVG and original screenshot collage remain linked. No external image assets or private records are used.

## Current enquiry and Leads captures — 27 October 2026

Actual browser captures of the normal API/database app on loopback port 8822, using a newly created disposable SQLite database and fictional Alex Morgan/review-sales accounts. Application code is c3bcfee; checkout base is 5d0b647 with audit-only docs/tests/rehearsal edits. No frontend/backend application changes or photo assets were introduced for these captures. They are not browser-demo images or hosted customer records. Earlier images remain dated above.

- customer-enquiry-20261027.jpg: lower portion of the vehicle enquiry popup, required inputs and explicitly selected optional email preference. The form then saved enquiry #2.
- customer-conversation-20261027.jpg: seeded enquiry #1's staff response and actual browser customer follow-up; internal diary note/task is absent.
- staff-actions-20261027.jpg: enquiry #2, compact action selector and the account reply form before saving the reply. Only the selected action form is open.
- leads-20261027.jpg: saved contact after enquiry #2 was closed, two grouped enquiries and the explicit opt-in history. No campaign was sent.

Browser actions also exercised the full #2 reply/customer-reply/schedule/complete/close sequence. The API regression separately asserts ownership/viewer/internal-note denials. Screenshots do not establish cross-device sharing, automated browser CI or production test writes. Source/result details: ../evidence/review-checkpoint-20261027.json.
