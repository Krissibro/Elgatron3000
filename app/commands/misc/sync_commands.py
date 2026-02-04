import discord
from discord import app_commands
from discord.ext import commands

from typing import Literal, Optional

from app.core.elgaTree import ElgatronError
from app.core.elgatron import Elgatron

class CommandSync(commands.Cog):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot

    @commands.is_owner()
    @app_commands.command(
        name="sync",
        description="Syncs commands"
    )
    async def sync(self, ctx: discord.Interaction, spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        await ctx.response.defer()

        # Owner check, only the owner can proceed
        if not await self.bot.is_owner(ctx.user):
            await ctx.edit_original_response(
                content="You do not have permission to use this command."
            )
            return
        
        guild = ctx.guild
        if guild is None:
            raise ElgatronError("The discord server is undefined (HOW???)")

        # Sync logic based on the 'spec' parameter
        if spec == "~":
            synced = await self.bot.tree.sync(guild=guild)
        elif spec == "*":
            self.bot.tree.copy_global_to(guild=guild)
            synced = await self.bot.tree.sync(guild=guild)
        elif spec == "^":
            self.bot.tree.clear_commands(guild=guild)
            await self.bot.tree.sync(guild=guild)
            synced = []
        else:
            synced = await self.bot.tree.sync(guild=guild)

        # Final response to indicate how many commands were synced
        await ctx.edit_original_response(
            content=f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )


# Set up the cog
async def setup(bot: Elgatron):
    await bot.add_cog(CommandSync(bot), guild=discord.Object(id=bot.guild_id))
