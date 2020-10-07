import os
import sys
import logging

from dotenv import load_dotenv

from dtl.bot import LeagueBot

logger = logging.getLogger(__name__)


def entrypoint():
    load_dotenv()
    debug = os.getenv("ENV") == "development"
    token = os.getenv("BOT_TOKEN")

    logging.basicConfig(level=logging.INFO)

    if token is None:
        logger.error("Specify a token you silly!")
        sys.exit(1)

    bot = LeagueBot(debug)
    logger.info("Starting bot!")
    bot.run(token)


if __name__ == "__main__":
    entrypoint()
