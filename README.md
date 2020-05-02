# SL? Are you DTL?

This is a Discord bot that mercilessly pings people when playing league of
legends.

## Developing Locally

1. Install [Poetry](https://python-poetry.org/).
2. Install dependencies. `poetry install`
3. Put secrets in `.env`.
4. Run the server. `poetry run python -m dtl.bot`

## Deploying on Heroku

1. Make a new app.
2. Enable worker dynos, or whatever it's called.
3. Add the buildpacks here: https://github.com/moneymeets/python-poetry-buildpack
4. Add `BOT_TOKEN` in the config vars.
5. Link the app with the repo.
6. Pray.
