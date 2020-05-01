import os
import logging

from dotenv import load_dotenv
import discord

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DADDY = 281527150765408256

THE_BADGER_HOLE = 326580881965842433
TBH_GENERAL = 326580881965842433
TBH_DEBUG_CHANNEL = 705667675292172288

SUITE = 428695150294859786
SL_CHANNEL = 615749992388362250

TOBY = 279068702995906562
JEREMY = 306074406235668480
FRANZ = 356508428358778891
DARSHAN = 284163385128386561
# guild = discord.utils.get(client.guilds, name='My Server')

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
    everyone = guild.default_role

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
        guild = message.guild
        discord_emoji = discord.utils.get(guild.emojis, name=emoji)
        if discord_emoji:
            await message.add_reaction(discord_emoji)
        else:
            logger.warning(f"emoji {emoji} was not found")

    if channel.id == TBH_DEBUG_CHANNEL:
        logger.debug(message)
        print(message.content)
        # feelsbadman = bot.get_emoji(440382843865006082)
        feelsbadman = discord.utils.get(guild.emojis, name="feelsbadman")
        mention = message.author.mention
        # emoji = discord.utils.get(guild.emojis, name='LUL')
        if author_id == DADDY:
            await channel.send(f"the bot speaks! {str(feelsbadman)} {mention}")
            await react_with("feelsbadman")
        # return

    await react_with("FeelsGoodMan")
    await channel.send(
        f"Attention everyone! "
        "{message.author.mention} would like to play some League! "
        ":ok_hand: "
        "Are you interested? "
        "(I've also pinged Darshan in the other server.)"
    )
    await channel.send(
        "To invoke this bot, just "
        "say something in this channel with the substring `SL?` or `DTL?` "
        "or mention me in this channel!"
    )
    if author_id == DADDY:
        await channel.send(
            "Oh look, Andrew pinged me. Hi daddy! :heart: :heart: :heart:"
        )

    downstream = bot.get_channel(TBH_DEBUG_CHANNEL)
    daddio = bot.get_user(DADDY)
    await downstream.send(f"{daddio.mention} League?")
    await downstream.send(f"{guild.owner.mention} valorant?")

    # if it's in SL of suite++
    # AND it's a relevant string
    # - react to the msg
    # - say something fun
    # - ping darshan on TBH


if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("BOT_TOKEN"))
