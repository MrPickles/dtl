# syntax=docker/dockerfile:1
FROM python:3.12-alpine
COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /uvx /bin/

RUN apk add build-base
RUN apk add libffi-dev

COPY . /app
WORKDIR /app

RUN uv sync --frozen --no-dev
ENTRYPOINT ["uv", "run", "bot"]
