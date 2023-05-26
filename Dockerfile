# syntax=docker/dockerfile:1
FROM python:3.10-alpine

RUN apk add build-base
RUN apk add libffi-dev
RUN pip install poetry

COPY . /app
WORKDIR /app

RUN poetry install --no-dev
ENTRYPOINT poetry run bot
