import logging
from typing import Optional, Callable, Any, List, Tuple
import re
import random

from humanize import naturaldelta  # type: ignore

from dtl.gifs import (
    pizza_time,
    troy_pizza_time,
    hacker,
    hackerman,
    mainframe,
    hacking_in_progress,
    hey_gurl,
    best_words,
    bitconnect,
    hey_bitch,
    terraria,
    elon_musk,
    triggered,
    mmm_mmm_no_no_no,
    bitconnect2,
    stonks,
)
from dtl.consts import ANDREW
from dtl.util import parse_timer

logger = logging.getLogger(__name__)

gif_config: List[Tuple[List[str], dict, Tuple[List[str], Optional[List[str]]]]] = [
    (["f"], {}, ([], ["press_f"])),
    (["nice"], {}, ([], ["nice"])),
    (["family", "time"], {"reducer": all}, ([terraria], ["thonk"])),
    (["pizza", "time"], {}, ([pizza_time, troy_pizza_time], ["🍕"])),
    (
        ["hack", "cyber"],
        {"cond": (lambda t, k: t.startswith(k))},
        ([hacker, hackerman, mainframe, hacking_in_progress], ["🤖"]),
    ),
    (["trump"], {}, ([best_words], ["🇺🇸", "🦅", "🍔"])),
    (["hi", "hey", "hello"], {}, ([hey_gurl, bitconnect, hey_bitch], ["👋"])),
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
]


def aram(_, message) -> Optional[Callable[[Any, Any], None]]:
    async def metasrc(_, message):
        tokens = message.content.lower().split(" ")
        champion = "".join(tokens[1:])
        champion = re.sub("[^a-z]", "", champion[:15])
        await message.channel.send(f"https://www.metasrc.com/{tokens[0]}/champion/{champion}")

    tokens = message.content.lower().split(" ")
    return metasrc if len(tokens) > 1 and tokens[0] in ["aram", "rift", "ofa", "urf", "blitz"] else None


def giphy_time(bot, message) -> Optional[Callable[[Any, Any], None]]:
    def gif_builder(gifs: List[str], emojis=None):
        async def gif_lambda(bot, message):
            if len(gifs) > 0 and not bot.is_rate_limited():
                bot.reset_rate_limit()
                await message.channel.send(random.choice(gifs))
            if emojis is not None:
                for emoji in emojis:
                    await bot.emoji_react(message, emoji)

        return gif_lambda

    if bot.user in message.mentions:
        return gif_builder([hey_gurl, bitconnect, hey_bitch], ["👋"])

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

    async def league_reminder(bot, message):
        await bot.emoji_react(message)
        emoji = await bot.emoji(message, game.lower())
        await message.channel.send(
            f"Hello @here! :wave: {message.author.mention} would like to play some {game}! {emoji}"
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
    if any(map(lambda x: x in tokens, ["sv", "dtv"])):
        game = "Valorant"
        return league_reminder
    return None
