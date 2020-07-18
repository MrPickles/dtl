import logging
from typing import Optional, Callable, Any
import re
import random

from humanize import naturaldelta  # type: ignore

from dtl.gifs import (
    pizza_time,
    hacker,
    hackerman,
    mainframe,
    hacking_in_progress,
    hey_gurl,
    best_words,
    bitconnect,
    hey_bitch,
    terraria,
)
from dtl.consts import ANDREW
from dtl.util import parse_timer

logger = logging.getLogger(__name__)


def aram(_, message) -> Optional[Callable[[Any, Any], None]]:
    async def metasrc(_, message):
        tokens = message.content.lower().split(" ")
        champion = "".join(tokens[1:])
        champion = re.sub("[^a-z]", "", champion[:15])
        if tokens[0] == "aram":
            await message.channel.send(
                f"https://www.metasrc.com/aram/champion/{champion}"
            )
        else:
            await message.channel.send(f"https://na.op.gg/champion/{champion}")

    tokens = message.content.lower().split(" ")
    return metasrc if len(tokens) > 1 and tokens[0] in ["aram", "rift"] else None


def giphy_time(bot, message) -> Optional[Callable[[Any, Any], None]]:
    def gif_builder(gifs, emojis=None):
        async def gif_lambda(bot, message):
            bot.reset_rate_limit()
            if emojis is not None:
                for emoji in emojis:
                    await bot.emoji_react(message, emoji)
            await message.channel.send(random.choice(gifs))

        return gif_lambda

    if bot.is_rate_limited():
        return None
    tokens = message.content.lower().split(" ")
    if all(map(lambda x: x in tokens, ["family", "time"])):
        return gif_builder([terraria], ["thonk"])
    if any(map(lambda x: x in tokens, ["pizza", "time"])):
        return gif_builder([pizza_time], ["🍕"])
    if any(map(lambda x: x in tokens, ["hacker"])):
        return gif_builder([hacker, hackerman, mainframe, hacking_in_progress], ["🤖"])
    if any(map(lambda x: x in tokens, ["trump"])):
        return gif_builder([best_words], ["🇺🇸", "🦅", "🍔"])
    if (
        any(map(lambda x: x in tokens, ["hi", "hey", "hello"]))
        or bot.user in message.mentions
    ):
        return gif_builder([hey_gurl, bitconnect, hey_bitch], ["👋"])
    return None


def shit_bot(_, message) -> Optional[Callable[[Any, Any], None]]:
    async def shit_bot_reaction(bot, message):
        await bot.emoji_react(message, "feelsbadman")

    tokens = message.content.lower().split(" ")
    if all(map(lambda x: x in tokens, ["shit", "bot"])):
        return shit_bot_reaction
    return None


def so_league(_, message) -> Optional[Callable[[Any, Any], None]]:
    async def league_reminder(bot, message):
        await bot.emoji_react(message)
        league = await bot.emoji(message, "league")
        await message.channel.send(
            f"Hello @here! :wave: {message.author.mention} would like to play some League! {league}"
        )
        if message.author.id == ANDREW:
            await message.channel.send(
                "Oh look, Andrew pinged me. Hi daddy! :heart: :heart: :heart:"
            )
        timediff = parse_timer(message.content)
        if timediff is not None:

            async def cb():
                logger.info("Starting callback!")
                await message.channel.send(
                    f":alarm_clock: {message.author.mention} set a timer {naturaldelta(timediff)} ago! Time to drop!"
                )

            await bot.remind_about_league(timediff, cb)

    if message.content[-1] != "?":
        return None
    tokens = message.content[:-1].lower().split(" ")
    if any(map(lambda x: x in tokens, ["sl", "dtl"])):
        return league_reminder
    return None
