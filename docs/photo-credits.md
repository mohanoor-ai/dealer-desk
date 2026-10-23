# Sample image credits and licences

The eleven bundled vehicle references are downloaded from Wikimedia Commons. Each image's photographer, original file page and specific licence URL are retained in `sample-assets/stock/credits.json` and in the database when attached. The relevant licence is CC BY-SA 4.0 or CC BY-SA 3.0 Germany as specified per image. Credit, source and licence links appear on the inventory cards and vehicle gallery.

Downloaded reference JPEGs retain their original photograph's licence. Application-generated versions are resized, recompressed, have metadata removed, and may be visually cropped by the card layout. These adaptations remain available under the same respective CC BY-SA licence. These photo licences cover the photos, not a blanket licence for the application code. No photographer or manufacturer endorsement is implied.

The images are illustrative, not photos of vehicles owned or offered for sale by this demo dealership. Exact model year, trim, engine, colour, market and badge may differ from the sample record. The Vauxhall example uses an Opel Corsa-e reference, explicitly described in its caption. The MINI reference is an electric J01 and is an illustration of the model family, not evidence of the petrol Classic specification.

## Photographers
- Ford Puma and Volkswagen Golf: Vauxford — CC BY-SA 4.0.
- Jaecoo J7 and MG HS: © M 93 — CC BY-SA 3.0 Germany.
- Kia Sportage: LuvsMG481 — CC BY-SA 4.0.
- Nissan Qashqai, MINI Hatch and Tesla Model 3: Alexander-93 — CC BY-SA 4.0.
- Opel Corsa-e: Alexander Migl — CC BY-SA 4.0.
- Volvo XC40: Elise240SX — CC BY-SA 4.0.

All original file and licence links are in the JSON manifest. The seed command attaches only to explicitly labelled sample vehicles and skips a source already attached. Existing uploaded photos are never replaced.

To attach the bundled references after creating sample stock: `uv run python -m scripts.seed_sample_photos --username manager --base-url http://127.0.0.1:8090`. The password is requested interactively. The command needs the running local application, but no internet download because the licensed files are bundled.

