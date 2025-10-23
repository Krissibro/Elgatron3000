import discord

from discord import app_commands
from discord.ext import commands

from bot import Elgatron
from commands.messaging.management.management_view import ManageCommandsDropDown
from utilities.settings import active_commands

class CommandManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="manage_commands",
        description="See and manage running commands"
    )
    async def manage_commands(self, ctx: discord.Interaction):
        if active_commands.is_empty():
            await ctx.response.send_message(embed=discord.Embed(title="No commands running",
                    color=discord.Color.red()), ephemeral=True)
            return
        view = ManageCommandsDropDown()
        first_embed = active_commands.make_overview_embed()
        await ctx.response.send_message(embed=first_embed, view=view, ephemeral=True)

    @app_commands.command(
        name="cleanup",
        description="Clean the current chat for bot messages"
    )
    async def cleanup(self, ctx: discord.Interaction, messages_amount: int):
        if messages_amount <= 0:
            await ctx.response.send_message(embed=discord.Embed(title="Cannot delete less than 1 message"),
                                            ephemeral=True)
            return
        await ctx.response.defer()
        await ctx.channel.purge(limit=messages_amount, check=lambda m: m.author == self.bot.user)
        await ctx.response.send_message(embed=discord.Embed(title=f"Deleted {messages_amount} messages"),
                                        ephemeral=True,
                                        delete_after=10)


async def setup(bot: Elgatron):
    await bot.add_cog(CommandManagement(bot), guild=discord.Object(id=bot.guild_id))