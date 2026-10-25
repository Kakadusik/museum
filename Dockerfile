# syntax=docker/dockerfile:1

# --- development backend (code is bind-mounted by docker-compose.yml) ---
FROM python:3.10-slim AS backend-dev
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
WORKDIR /app/backend
EXPOSE 8000
CMD ["python", "app.py"]

# --- production frontend build ---
FROM oven/bun:1 AS frontend-build
ENV BUN_INSTALL=/usr/local
WORKDIR /src/frontend
COPY frontend/ ./
RUN bun add -g nuekit@2.0.0-beta.2 && nue build --clean

# --- production runtime ---
FROM python:3.10-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    DEBUG=0 \
    AUTO_RELOAD=0 \
    FRONTEND_DIST=/app/frontend/.dist
WORKDIR /app
RUN groupadd --system museum \
    && useradd --system --gid museum --no-create-home --shell /usr/sbin/nologin museum
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY --from=frontend-build /src/frontend/.dist ./frontend/.dist
USER museum
WORKDIR /app/backend
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=5 \
    CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2).status == 200 else 1)"
CMD ["python", "app.py"]
