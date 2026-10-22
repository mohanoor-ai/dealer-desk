# Offline operation — current boundary

The main application and built React files do not require a cloud AI service. The companion HTML and Markdown open without a server or CDN.

Initial setup requires internet for Docker base images, PostgreSQL, Python wheels and npm packages. `docker compose up --build` needs those downloads; it is not an offline preparation guarantee by itself.

For a prepared Docker installation: build the app and pull PostgreSQL while online. Retain the built image and database volume. Save both images with `docker save -o <private-preparation-folder>/dealer-images.tar <app-image-tag> postgres:16-alpine`. On another compatible machine with Docker installed, use `docker load -i <folder>/dealer-images.tar`. Match the CPU architecture. Start with `docker compose up -d --no-build --pull never` after selecting the prepared app image in a deployment override. The portable override and automated preparation script remain to be delivered and verified.

Do not treat npm's cache or an existing virtual environment as a portable dependency bundle. A full offline Python wheelhouse must target the destination OS/Python/CPU. No local AI model is installed or required. A future local model option would need a separately downloaded model and measured RAM/CPU/GPU requirements.
