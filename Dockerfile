FROM node:26-bookworm-slim AS web-build
WORKDIR /build/apps/web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM python:3.13-slim-bookworm AS python-build
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN python -m pip install --upgrade pip build && python -m build --wheel

FROM python:3.13-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FAULTGRAPH_DATABASE_PATH=/data/faultgraph.db \
    FAULTGRAPH_STATIC_DIRECTORY=/app/static \
    FAULTGRAPH_ALLOWED_ORIGINS='[]' \
    FAULTGRAPH_ENVIRONMENT=production
RUN groupadd --system --gid 10001 faultgraph \
    && useradd --system --uid 10001 --gid faultgraph --home-dir /nonexistent faultgraph \
    && mkdir -p /app/static /data \
    && chown faultgraph:faultgraph /data
COPY --from=python-build /build/dist/ /tmp/wheels/
RUN python -m pip install --no-cache-dir /tmp/wheels/*.whl && rm -r /tmp/wheels
COPY --from=web-build /build/apps/web/dist/ /app/static/
USER 10001:10001
WORKDIR /app
EXPOSE 8000
VOLUME ["/data"]
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)"]
CMD ["uvicorn", "faultgraph.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
