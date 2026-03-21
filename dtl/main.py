import os
import sys
import logging

import subprocess
from dotenv import load_dotenv
import discord
import humanize
from datetime import datetime

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

    @bot.tree.command(name="health", description="Get vitals about the bot")
    async def health_command(interaction: discord.Interaction):
        commit_sha = os.getenv("COMMIT_SHA", "unknown")

        if commit_sha == "unknown":
            try:
                commit_sha = subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"], text=True
                ).strip()
            except Exception:
                pass

        uptime = datetime.now() - interaction.client.start_time
        uptime_str = humanize.precisedelta(uptime, minimum_unit="seconds")

        embed = discord.Embed(title="Bot Health", color=discord.Color.green())
        embed.add_field(name="Build Hash", value=commit_sha, inline=False)
        embed.add_field(name="Uptime", value=uptime_str, inline=False)

        await interaction.response.send_message(embed=embed)

    logger.info("Starting bot!")
    bot.run(token)


if __name__ == "__main__":
    entrypoint()
