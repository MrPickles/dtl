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
from dtl.util import this_person_wants_to_play_league, parse_timer

logger = logging.getLogger(__name__)


class LeagueBot(discord.Client):
    pending_reminder: Optional[aio.Task] = None

    async def on_ready(self):
        logger.info("Logged in as %s with ID %s", self.user.name, self.user.id)
        logger.info("Bot is ready to receive messages!")

    async def on_message(self, message):
        guild = message.guild
        channel = message.channel
        author_id = message.author.id
        badger_hole = self.get_channel(TBH_GENERAL_CHANNEL)
        darshan = self.get_user(DARSHAN)

        async def react_with(emoji: str):
            discord_emoji = discord.utils.get(guild.emojis, name=emoji)
            if discord_emoji:
                await message.add_reaction(discord_emoji)
            else:
                logger.warning("emoji {emoji} was not found", emoji=emoji)

        if self.user in message.mentions:
            # This is very messy. Clean it up later.
            logger.info("Pizza time!")
            await react_with("feelsgoodman")
            await channel.send("https://tenor.com/bgq1G.gif")
            return

        if author_id == self.user.id or channel.id not in [
            TBH_DEBUG_CHANNEL,
            SL_CHANNEL,
        ]:
            return

        if not this_person_wants_to_play_league(message.content):
            return

        # To avoid spamming.
        if channel.id == TBH_DEBUG_CHANNEL:
            badger_hole = self.get_channel(TBH_DEBUG_CHANNEL)
            darshan = self.get_user(ANDREW)

        logger.info(message)

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

        # Interact with Suite++
        await react_with("feelsgoodman")
        await channel.send(
            f"Hello @here! :wave: "
            f"{message.author.mention} would like to play some League! "
            f"(I've also pinged Darshan in the other server. :100:)"
        )

        timediff = parse_timer(message.content)

        async def maybe_send_reminder_msg(discord_channel, pronoun: str) -> None:
            if timediff is None:
                return

            await discord_channel.send(
                f"My proprietary state-of-the-art AI-powered NLP algorithm has "
                f"detected that {pronoun} would like to play in approximately "
                f"{naturaldelta(timediff)}. I'll remind you then! :timer:"
            )

        await maybe_send_reminder_msg(channel, "you")
        if timediff is not None:
            if self.pending_reminder is not None:
                # Cancel any pending reminders.
                self.pending_reminder.cancel()
            # Create a coroutine to remind the channel.
            self.pending_reminder = aio.create_task(remind_about_league(timediff))

        await channel.send(
            "To get my attention, :robot: just "
            "ask a question in this channel with the substring `SL` or `DTL` "
            "or mention me in this channel."
        )

        if author_id == ANDREW:
            await channel.send(
                "Oh look, Andrew pinged me. Hi daddy! :heart: :heart: :heart:"
            )

        # Interact with The Badger Hole
        await badger_hole.send(
            f"Hello {darshan.mention}! :wave: {message.author.mention} wonders "
            "if you're interested in some League!"
        )
        await maybe_send_reminder_msg(badger_hole, "he")
