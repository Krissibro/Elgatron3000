from discord import Interaction
import discord
from discord.app_commands import CommandTree
from discord.app_commands.errors import AppCommandError, TransformerError

from utilities.errors import ElgatronError

class ElgaTree(CommandTree):
    async def on_error(self, interaction: Interaction, error: AppCommandError) -> None:
        """
        Centralized error handler for cog commands.
        Call this from any cog's cog_app_command_error method.
        """
        original_error = getattr(error, 'original', error)

        embed = discord.Embed(description=f"{original_error}", color=discord.Color.red())

        # Send error message (handle if already responded)
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.HTTPException:
            # Silently fail if we can't send the error message
            pass

        if not isinstance(original_error, (ElgatronError, TransformerError)):
            embed.title = "An error occurred!"
            await super().on_error(interaction, error)