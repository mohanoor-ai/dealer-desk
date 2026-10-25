FROM node:24-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Public article sources and credited images are bundled by Vite.
COPY docs/articles/ /docs/articles/
COPY docs/media/ /docs/media/
COPY docs/evidence/ /docs/evidence/
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home dealer
COPY backend/ backend/
COPY migrations/ migrations/
COPY scripts/ scripts/
COPY alembic.ini start.py ./
COPY --from=frontend /frontend/dist frontend/dist
USER dealer
EXPOSE 8090
CMD ["python", "start.py", "--host", "0.0.0.0"]
