import os
import logging

from dotenv import load_dotenv
import discord

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


def this_person_wants_to_play_league(msg):
    keywords = ["sl?", "dtl?"]
    return any(map(lambda x: x in msg.lower(), keywords))


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user.name} with ID {bot.user.id}")
    logger.info("Bot is ready to receive messages!")


@bot.event
async def on_message(message):
    guild = message.guild
    channel = message.channel
    author_id = message.author.id

    if author_id == bot.user.id:
        return

    if channel.id not in [TBH_DEBUG_CHANNEL, SL_CHANNEL]:
        return

    if (
        not this_person_wants_to_play_league(message.content)
        and bot.user not in message.mentions
    ):
        return

    async def react_with(emoji: str):
        discord_emoji = discord.utils.get(guild.emojis, name=emoji)
        if discord_emoji:
            await message.add_reaction(discord_emoji)
        else:
            logger.warning(f"emoji {emoji} was not found")

    await react_with("FeelsGoodMan")
    await channel.send(
        f"Hello @here! :wave: "
        f"{message.author.mention} would like to play some League! "
        f"Are you interested? "
        f"(I've also pinged Darshan in the other server. :100:)"
    )
    await channel.send(
        "To get my attention, :robot: just "
        "say something in this channel with the substring `SL?` or `DTL?` "
        "or mention me in this channel."
    )
    if author_id == ANDREW:
        await channel.send(
            "Oh look, Andrew pinged me. Hi daddy! :heart: :heart: :heart:"
        )

    badger_hole = bot.get_channel(TBH_GENERAL_CHANNEL)
    darshan = bot.get_user(DARSHAN)
    await badger_hole.send(f"{darshan.mention} League?")


if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("BOT_TOKEN"))
