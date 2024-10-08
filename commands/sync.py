import discord
from discord import app_commands
from discord.ext import commands
from utilities.settings import guild_id
from typing import Literal, Optional


class CommandSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        # Sync logic based on the 'spec' parameter
        if spec == "~":
            synced = await self.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await self.bot.tree.sync()

        # Final response to indicate how many commands were synced
        await ctx.edit_original_response(
            content=f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )


# Set up the cog
async def setup(bot):
    await bot.add_cog(CommandSync(bot), guild=bot.get_guild(guild_id))
