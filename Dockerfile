# ---------- Stage 1: build the React frontend ----------
FROM node:20-alpine AS frontend
WORKDIR /fe
COPY arcade-frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY arcade-frontend/ ./
# Same-origin API calls (served by FastAPI below)
ENV VITE_API_URL=""
RUN npm run build

# ---------- Stage 2: Python backend + static frontend ----------
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY arcade-backend/requirements.txt .
RUN pip install -r requirements.txt

COPY arcade-backend/ .
# Drop built SPA where main.py looks for it
COPY --from=frontend /fe/dist ./static

EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
