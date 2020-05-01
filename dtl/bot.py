import os
import asyncio

from dotenv import load_dotenv
import discord

DADDY = 281527150765408256
THE_BADGER_HOLE = 326580881965842433
# guild = discord.utils.get(client.guilds, name='My Server')

bot = discord.Client()


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")
    print(bot.guilds)
    guild = discord.utils.get(bot.guilds, name="The Badger Hole")
    if guild is not None:
        channel = discord.utils.get(guild.text_channels, name="debug")
        print(channel)
        print(type(channel))


@bot.event
async def on_message(message):
    print(message)
    print(message.content)
    channel = message.channel
    author_id = message.author.id
    feelsbadman = bot.get_emoji(440382843865006082)
    if author_id == DADDY:
        await channel.send(f"the bot speaks! {str(feelsbadman)}")
        await message.add_reaction(feelsbadman)
    if author_id == bot.user.id:
        print("this bot spoke")


if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("BOT_TOKEN"))
