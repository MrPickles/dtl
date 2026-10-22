import discord
from discord import app_commands

from dtl.util import spongebob_text


@app_commands.command(
    name="spongebob", description="Convert text to mocking SpongeBob case"
)
@app_commands.describe(text="The text to convert")
async def spongebob_command(
    interaction: discord.Interaction, text: app_commands.Range[str, 1, 1000]
):
    result = spongebob_text(text)
    if not result.strip():
        await interaction.response.send_message(
            "Please enter some text to convert.", ephemeral=True
        )
        return
    if len(result) > 2000:
        await interaction.response.send_message(
            "The converted text is too long. Please use shorter text.", ephemeral=True
        )
        return
    await interaction.response.send_message(
        result, allowed_mentions=discord.AllowedMentions.none()
    )
