from datetime import datetime, timedelta
import logging
from typing import Optional, Callable, Any, List, Tuple
import re
import random

import discord  # type: ignore
from humanize import naturaldelta  # type: ignore

from dtl.gifs import (
    pizza_time,
    troy_pizza_time,
    hayasaka,
    bitconnect,
    hey_bitch,
    terraria,
    elon_musk,
    triggered,
    mmm_mmm_no_no_no,
    bitconnect2,
    stonks,
    very_nice,
    nice_to_meet_you,
    cheesesteak_joe,
    chainwax,
    lets_play_catan,
    catan_ragequit,
    calm_down,
    not_stonks,
)
from dtl.consts import (
    ANDREW,
    TBH_DEBUG_CHANNEL,
    TBH_SUMMONER_ROLE,
    TBH_GENERAL_CHANNEL,
    STONKS_CHANNEL,
    SUITE_GENERAL_CHANNEL,
    POGO_CHANNEL,
    POLITICS_CHANNEL,
)

from dtl.util import parse_timer

logger = logging.getLogger(__name__)

greeting_gifs = [nice_to_meet_you, hayasaka, bitconnect, hey_bitch]
gif_config: List[Tuple[List[str], dict, Tuple[List[str], Optional[List[str]]]]] = [
    (["f"], {}, ([], ["press_f"])),
    (["very", "nice"], {"reducer": all}, ([very_nice], ["nice"])),
    (["not", "stonks"], {"reducer": all}, ([not_stonks], ["📉"])),
    (["nice"], {}, ([], ["nice"])),
    (
        ["family", "time"],
        {"reducer": all},
        ([terraria, lets_play_catan, catan_ragequit], ["thonk"]),
    ),
    (["pizza"], {}, ([pizza_time, troy_pizza_time], ["🍕"])),
    (["elon", "musk", "simulation", "tesla"], {}, ([elon_musk], ["🚭"])),
    (
        ["trigger"],
        {"cond": (lambda t, k: t.startswith(k))},
        ([triggered], ["⚠️", "🚨", "☢️"]),
    ),
    (
        ["bitcoin", "bitconnect", "dogecoin", "cryptocurrency"],
        {},
        ([bitconnect, mmm_mmm_no_no_no, bitconnect2], ["📈"]),
    ),
    (["yikes"], {}, ([], ["😬"])),
    (["stonk", "stonks"], {}, ([stonks], ["📈"])),
    (["shit", "bot"], {"reducer": all}, ([], ["feelsbadman"])),
    (["good", "bot"], {"reducer": all}, ([], ["feelsgoodman"])),
    (["cheesesteak", "philly"], {}, ([cheesesteak_joe], [])),
    (["pussy", "chainwax", "chain"], {}, ([chainwax], [])),
]


def censor(_, message) -> Optional[Callable[[Any, Any], None]]:
    if message.channel.id not in [SUITE_GENERAL_CHANNEL, TBH_DEBUG_CHANNEL]:
        return None
    tokens = set(message.content.lower().split(" "))
    target_channel = None
    if bool(set(["trump", "biden", "aoc", "antifa"]) & tokens):
        target_channel = POLITICS_CHANNEL
    elif bool(set(["raid", "shiny"]) & tokens):
        target_channel = POGO_CHANNEL
    elif bool(set(["gme", "stocks", "moon", "gamestop", "tsla"]) & tokens):
        target_channel = STONKS_CHANNEL

    if target_channel is None:
        return None

    async def safe_space(bot, message):
        suggested_channel = bot.get_channel(target_channel)
        await message.channel.send(
            f":rotating_light: This channel is a safe space! Consider talking in {suggested_channel.mention} instead. :rotating_light:"
        )

    return safe_space


def aram(_, message) -> Optional[Callable[[Any, Any], None]]:
    async def metasrc(_, message):
        tokens = message.content.lower().split(" ")
        champion = "".join(tokens[1:])
        champion = re.sub("[^a-z]", "", champion[:15])
        await message.channel.send(
            f"https://www.metasrc.com/{tokens[0]}/champion/{champion}"
        )

    tokens = message.content.lower().split(" ")
    return (
        metasrc
        if len(tokens) > 1 and tokens[0] in ["aram", "rift", "ofa", "urf", "blitz"]
        else None
    )


def silence(_, message) -> Optional[Callable[[Any, Any], None]]:
    async def silence_bot(bot, _):
        if bot.last_gif_msg is not None:
            await bot.last_gif_msg.delete()
            bot.last_gif_msg = None
            bot.reset_rate_limit(datetime.now() + timedelta(hours=1))
            await message.channel.send(
                "Sorry about that. I won't send gifs for the next hour. 😓"
            )
        await bot.emoji_react(message, "feelsbadman")

    return silence_bot if message.content.lower() == "shut up bot" else None


def giphy_time(bot, message) -> Optional[Callable[[Any, Any], None]]:
    def gif_builder(gifs: List[str], emojis: List[str] = None):
        async def gif_lambda(bot, message):
            if len(gifs) > 0 and not bot.is_rate_limited():
                bot.reset_rate_limit()
                bot.last_gif_msg = await message.channel.send(random.choice(gifs))
            if emojis is not None:
                for emoji in emojis:
                    await bot.emoji_react(message, emoji)

        return gif_lambda

    if bot.user in message.mentions:
        return gif_builder(greeting_gifs, ["👋"])

    if "69" in message.content:
        return gif_builder([], ["nice"])

    tokens = re.sub("[^a-z ]", "", message.content.lower()).split(" ")

    def check(keywords, cond=lambda t, k: t == k, reducer=any) -> bool:
        return reducer(map(lambda k: any(map(lambda t: cond(t, k), tokens)), keywords))

    for config in gif_config:
        keywords, kwargs, args = config
        if check(keywords, **kwargs):
            return gif_builder(*args)

    return None


def so_league(_, message) -> Optional[Callable[[Any, Any], None]]:
    game = "League"

    def mention_for_channel(message) -> str:
        mention_map = {
            TBH_DEBUG_CHANNEL: TBH_SUMMONER_ROLE,
            TBH_GENERAL_CHANNEL: TBH_SUMMONER_ROLE,
        }
        if message.channel.id in mention_map:
            role_id = mention_map[message.channel.id]
            role = discord.utils.get(message.guild.roles, id=role_id)
            if role is not None:
                return role.mention
            logger.warning("Fetching role ID %d failed!", role_id)
        return "@here"

    async def league_reminder(bot, message):
        await bot.emoji_react(message)
        emoji = await bot.emoji(message, game.lower())
        mention = mention_for_channel(message)

        if message.author.id == ANDREW:
            await message.channel.send(
                "Andrew has a gaming addiction. Let's have someone else suggest playing games..."
            )
            await message.channel.send(calm_down)
            return
        await message.channel.send(
            f"Hello {mention}! :wave: {message.author.mention} would like to play some {game}! {emoji}"
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
    if any(map(lambda x: x in tokens, ["sv", "dtv"])):
        game = "Valorant"
        return league_reminder
    return None
