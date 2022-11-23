# League Bot

This is a Discord bot that mercilessly pings people when playing League of
Legends.

## Running with Docker

There's a Docker image for this bot:
https://hub.docker.com/repository/docker/liuandrewk/dtl

To run it, you'll need a `BOT_TOKEN` specified as an environment variable.

```shell
docker run -it -e BOT_TOKEN=${BOT_TOKEN} docker.io/liuandrewk/dtl
```

## Developing Locally

1. Install [Poetry](https://python-poetry.org/).
2. Install dependencies. `poetry install`
3. Put secrets in `.env`.
4. Run the server. `poetry run bot`
5. If you want to make commits, please install the precommit hooks.
   `poetry run pre-commit install`

## Deploying on Heroku

1. Make a new app.
2. Enable worker dynos.
3. Add the buildpacks here: https://github.com/moneymeets/python-poetry-buildpack
4. Add `BOT_TOKEN` in the config vars.
5. Link the app with the repo.
6. To check logs, you can use Heroku's CLI: `heroku logs -a your-app-name-here -t`

## Developing with Docker

Below are the commands to build and push the docker image:

```shell
docker build -t liuandrewk/dtl .
docker push liuandrewk/dtl
```
