import discord
from discord import app_commands
from discord.ext import commands
from utilities.settings import guild_id
from typing import Literal, Optional


class CommandSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html
    @commands.is_owner()
    @app_commands.command(
        name="sync",
        description="syncs commands"
    )
    async def sync(self, ctx: discord.Interaction, spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        await ctx.response.defer()

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

        await ctx.edit_original_response(
            content=f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return


async def setup(bot):
    await bot.add_cog(CommandSync(bot), guild=bot.get_guild(guild_id))
