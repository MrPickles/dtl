# syntax=docker/dockerfile:1
FROM python:3.11.3-alpine3.18

RUN apk add build-base
RUN apk add libffi-dev
RUN pip install poetry

COPY . /app
WORKDIR /app

RUN poetry install --no-dev
ENTRYPOINT poetry run bot
