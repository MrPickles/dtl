import logging
from datetime import timedelta
from typing import Optional
import asyncio as aio

import discord  # type: ignore
from humanize import naturaldelta  # type: ignore

from dtl.consts import (
    ANDREW,
    TBH_GENERAL_CHANNEL,
    TBH_DEBUG_CHANNEL,
    SL_CHANNEL,
    DARSHAN,
)
from dtl.util import this_person_wants_to_play_league, parse_timer, is_pizza_time

logger = logging.getLogger(__name__)


class LeagueBot(discord.Client):
    pending_reminder: Optional[aio.Task] = None

    def __init__(self, debug: bool = False):
        super().__init__()
        self.debug = debug

    async def on_ready(self):
        logger.info("Logged in as %s with ID %s", self.user.name, self.user.id)
        logger.info("Debug mode=%s", self.debug)
        logger.info("Bot is ready to receive messages!")
        if not self.debug:
            debug_channel = self.get_channel(TBH_DEBUG_CHANNEL)
            andrew = self.get_user(ANDREW)
            await debug_channel.send(f"{andrew.mention} New bot successfully deployed!")

    async def on_message(self, message):
        logger.info(message)

        # Don't interact with self.
        if message.author.id == self.user.id:
            return

        # Pizza time!
        if self.user in message.mentions or is_pizza_time(message.content):
            await LeagueBot._pizza_time_handler(message)
            return

        # Only interact with specific channels.
        if message.channel.id not in [TBH_DEBUG_CHANNEL, SL_CHANNEL]:
            return

        # Droppin' time!
        if this_person_wants_to_play_league(message.content):
            await self._dtl_handler(message)
            return

    async def _dtl_handler(self, message):
        channel = message.channel
        badger_hole = self.get_channel(TBH_GENERAL_CHANNEL)
        darshan = self.get_user(DARSHAN)

        # To avoid spamming.
        if self.debug:
            channel = badger_hole = self.get_channel(TBH_DEBUG_CHANNEL)
            darshan = self.get_user(ANDREW)

        async def remind_about_league(duration: timedelta) -> None:
            try:
                logger.info(
                    "Coroutine started! Waiting %d seconds...", duration.total_seconds()
                )
                await aio.sleep(duration.total_seconds())
                await badger_hole.send(
                    ":alarm_clock: This is a reminder that "
                    f"{message.author.mention} expressed interest in League "
                    f"{naturaldelta(duration)} ago! Are we droppin'?"
                )
                self.pending_reminder = None
                logger.info("Coroutine completed!")
            except aio.CancelledError:
                logger.info("Coroutine was cancelled!")
                await channel.send(
                    "(As FYI, I already had an active reminder. "
                    "The old reminder has been cancelled.)"
                )

        async def send_reminder_msg(timediff, discord_channel, pronoun: str) -> None:
            await discord_channel.send(
                f"My proprietary state-of-the-art AI-powered NLP algorithm has "
                f"detected that {pronoun} would like to play in approximately "
                f"{naturaldelta(timediff)}. I'll remind you then! :timer:"
            )

        # Interact with Suite++
        await self._emoji_react(message)
        await channel.send(
            f"Hello @here! :wave: "
            f"{message.author.mention} would like to play some League! "
            f"(I've also pinged Darshan in the other server. :100:)"
        )
        await channel.send(
            "To get my attention, :robot: just "
            "ask a question in this channel with the substring `SL` or `DTL` "
            "or mention me in this channel."
        )
        if message.author.id == ANDREW:
            await channel.send(
                "Oh look, Andrew pinged me. Hi daddy! :heart: :heart: :heart:"
            )

        # Interact with The Badger Hole
        await badger_hole.send(
            f"Hello {darshan.mention}! :wave: {message.author.mention} wonders "
            "if you're interested in some League!"
        )

        # Send timing message and set reminder.
        timediff = parse_timer(message.content)
        if timediff is not None:
            await send_reminder_msg(timediff, channel, "you")
            await send_reminder_msg(timediff, badger_hole, "he")
            if self.pending_reminder is not None:
                # Cancel any pending reminders.
                self.pending_reminder.cancel()
            # Create a coroutine to remind the channel.
            self.pending_reminder = aio.create_task(remind_about_league(timediff))

    @staticmethod
    async def _pizza_time_handler(message):
        logger.info("Pizza time!")
        await LeagueBot._emoji_react(message)
        await message.channel.send("https://tenor.com/bgq1G.gif")

    @staticmethod
    async def _emoji_react(message, emoji: str = "feelsgoodman"):
        discord_emoji = discord.utils.get(message.guild.emojis, name=emoji)
        if not discord_emoji:
            logger.warning("emoji {emoji} was not found", emoji=emoji)
            return
        await message.add_reaction(discord_emoji)
