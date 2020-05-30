import os
import logging
from datetime import timedelta
from typing import Optional
import asyncio as aio

from dotenv import load_dotenv
import discord  # type: ignore
from humanize import naturaldelta  # type: ignore

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ANDREW = 281527150765408256

THE_BADGER_HOLE = 326580881965842433
TBH_GENERAL_CHANNEL = 326580881965842433
TBH_DEBUG_CHANNEL = 705667675292172288

SUITE = 428695150294859786
SL_CHANNEL = 615749992388362250

TOBY = 279068702995906562
JEREMY = 306074406235668480
FRANZ = 356508428358778891
DARSHAN = 284163385128386561

bot = discord.Client()
pending_reminder: Optional[aio.Task] = None


def this_person_wants_to_play_league(msg: str) -> bool:
    keywords = ["sl", "dtl"]
    return any(map(lambda x: x in msg.lower(), keywords)) and msg[-1] == "?"


def parse_timer(msg: str) -> Optional[timedelta]:
    in_split = msg.split(" in ")
    if len(in_split) != 2:
        logger.debug('No substring of "in" detected...')
        return None

    space_split = in_split[1].split(" ")
    if len(space_split) != 2:
        logger.debug("Time and unit wasn't split by a space")
        return None

    try:
        value = float(space_split[0])
    except ValueError as e:
        logger.debug("Numerical value failed to parse: %s", e)
        return None

    if value < 1:
        logger.debug("Duration is not positive: %s", value)
        return None

    full_unit = space_split[1]
    unit = full_unit[0].lower()
    if unit == "h" and value <= 3:
        return timedelta(hours=value)

    if unit == "m" and value >= 5:
        return timedelta(minutes=value)

    logger.debug(
        "Time unit didn't parse (%s) or value was out of bounds (%s)", full_unit, value
    )
    return None


@bot.event
async def on_ready():
    logger.info("Logged in as %s with ID %s", bot.user.name, bot.user.id)
    logger.info("Bot is ready to receive messages!")


@bot.event
async def on_message(message):
    guild = message.guild
    channel = message.channel
    author_id = message.author.id
    badger_hole = bot.get_channel(TBH_GENERAL_CHANNEL)
    darshan = bot.get_user(DARSHAN)

    async def react_with(emoji: str):
        discord_emoji = discord.utils.get(guild.emojis, name=emoji)
        if discord_emoji:
            await message.add_reaction(discord_emoji)
        else:
            logger.warning("emoji {emoji} was not found", emoji=emoji)

    if author_id == bot.user.id or channel.id not in [TBH_DEBUG_CHANNEL, SL_CHANNEL]:
        return

    if bot.user in message.mentions:
        # This is very messy. Clean it up later.
        logger.info("Pizza time!")
        await react_with("feelsgoodman")
        await channel.send("https://tenor.com/bgq1G.gif")
        return

    if not this_person_wants_to_play_league(message.content):
        return

    # To avoid spamming.
    if channel.id == TBH_DEBUG_CHANNEL:
        badger_hole = bot.get_channel(TBH_DEBUG_CHANNEL)
        darshan = bot.get_user(ANDREW)

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
            global pending_reminder  # pylint: disable=global-statement
            pending_reminder = None
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
        global pending_reminder  # pylint: disable=global-statement
        if pending_reminder is not None:
            # Cancel any pending reminders.
            pending_reminder.cancel()
        # Create a coroutine to remind the channel.
        pending_reminder = aio.create_task(remind_about_league(timediff))

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


if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("BOT_TOKEN"))
