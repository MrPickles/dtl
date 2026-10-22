import discord
from discord import app_commands
from typing import Optional

from dtl.util import spongebob_text


@app_commands.command(
    name="spongebob", description="Convert text to mocking SpongeBob case"
)
@app_commands.describe(text="Text to convert; omit to use the latest chat message")
async def spongebob_command(
    interaction: discord.Interaction,
    text: Optional[app_commands.Range[str, 1, 1000]] = None,
):
    send = interaction.response.send_message
    if text is None:
        await interaction.response.defer(thinking=True)
        send = interaction.followup.send
        channel = interaction.channel
        if channel is None or not hasattr(channel, "history"):
            await send("I can't read messages in this channel.", ephemeral=True)
            return
        try:
            async for message in channel.history(
                limit=50, before=interaction.created_at
            ):
                if not message.author.bot and message.content.strip():
                    text = message.content
                    break
        except discord.HTTPException:
            await send(
                "I couldn't read channel history. Check my View Channel and Read Message History permissions, or provide text.",
                ephemeral=True,
            )
            return
        if text is None:
            await send(
                "No recent text message found. Please provide text to convert.",
                ephemeral=True,
            )
            return
    result = spongebob_text(text)
    if not result.strip():
        await send("Please enter some text to convert.", ephemeral=True)
        return
    if len(result) > 2000:
        await send(
            "The converted text is too long. Please use shorter text.", ephemeral=True
        )
        return
    await send(result, allowed_mentions=discord.AllowedMentions.none())
