import logging
from datetime import datetime, timedelta
from typing import Optional, List, Callable, Any
import asyncio as aio
import random

import discord  # type: ignore

from dtl.consts import TBH_DEBUG_CHANNEL
from dtl.triggers import aram, giphy_time, so_league, silence

logger = logging.getLogger(__name__)

config: List[Callable[[Any, Any], Optional[Callable[[Any, Any], None]]]] = [
    silence,
    aram,
    giphy_time,
    so_league,
]


class LeagueBot(discord.Client):
    def __init__(self, debug: bool = False):
        super().__init__()
        self.debug = debug
        self.pending_reminder: Optional[aio.Task] = None
        self.rate_limit: datetime = datetime.utcfromtimestamp(0)
        self.last_gif_msg = None
        random.seed()

    async def on_ready(self):
        logger.info("Logged in as %s with ID %s", self.user.name, self.user.id)
        logger.info("Debug mode=%s", self.debug)
        logger.info("Bot is ready to receive messages!")

    async def on_message(self, message):
        # Don't interact with self.
        if message.author.id == self.user.id:
            return

        if self.debug != (message.channel.id == TBH_DEBUG_CHANNEL):
            return

        for trigger in config:
            action = trigger(self, message)
            if action is not None:
                await action(self, message)
                return

    def is_rate_limited(self, limit: int = 900) -> bool:
        if self.debug:
            limit = 2
        return (datetime.now() - self.rate_limit).total_seconds() < limit

    def reset_rate_limit(self, when: datetime = datetime.now()) -> None:
        self.rate_limit = when

    async def remind_about_league(
        self, duration: timedelta, callback, on_cancelled=None
    ) -> None:
        if self.debug:
            duration = timedelta(seconds=5)

        async def reminder():
            try:
                logger.info("Waiting %d seconds", duration.total_seconds())
                await aio.sleep(duration.total_seconds())
                logger.info("Starting callback!")
                await callback()
                self.pending_reminder = None
                logger.info("Coroutine completed!")
            except aio.CancelledError:
                logger.info("Coroutine was cancelled!")

        if self.pending_reminder is not None:
            # Cancel any pending reminders.
            logger.info("Cancelling pending coroutine!")
            self.pending_reminder.cancel()
            if on_cancelled is not None:
                await on_cancelled()
        # Create a coroutine to remind the channel.
        self.pending_reminder = aio.create_task(reminder())

    async def emoji(self, message, emoji: str):
        if len(emoji) < 2:
            # Don't waste time searching; it has to be a default emoji.
            return emoji
        discord_emoji = discord.utils.get(message.guild.emojis, name=emoji)
        return discord_emoji if discord_emoji else emoji

    async def emoji_react(self, message, emoji: str = "feelsgoodman"):
        discord_emoji = await self.emoji(message, emoji)
        try:
            await message.add_reaction(discord_emoji)
        except discord.errors.HTTPException:
            logger.warning("emoji %s was not found", emoji)
