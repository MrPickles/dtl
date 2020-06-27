import os
import logging

from dotenv import load_dotenv

from dtl.bot import LeagueBot

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG)
    bot = LeagueBot()
    logger.info("Sup dawg")
    bot.run(os.getenv("BOT_TOKEN"))
