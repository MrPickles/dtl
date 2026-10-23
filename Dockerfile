# syntax=docker/dockerfile:1
FROM python:3.12-alpine
COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /uvx /bin/

RUN apk add build-base
RUN apk add libffi-dev

COPY . /app
WORKDIR /app

ARG COMMIT_SHA="unknown"
ENV COMMIT_SHA=${COMMIT_SHA}

RUN uv sync --frozen --no-dev
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.build_opener(urllib.request.ProxyHandler({})).open('http://127.0.0.1:8080/health', timeout=3).close()"]
ENTRYPOINT ["uv", "run", "bot"]
