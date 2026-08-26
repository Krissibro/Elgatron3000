import asyncio

import discord
from discord.ext import commands
from discord import app_commands, Message

from utilities.elgatron import Elgatron

# :white_check_mark:, ":x:", :expressionless:, :person_shrugging:, :melting:, :date:
INTEREST_REACTIONS = ["✅", "❌", "😑", "🤷", "🫠", "📅"]

class ReactionCommands(commands.Cog):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot

        self.add_reactions_menu = app_commands.ContextMenu(
            name="Add interest reactions",
            callback=self.add_reactions_to_message,
        )

        # Required when a context menu belongs to a cog
        self.bot.tree.add_command(
            self.add_reactions_menu,
            guild=discord.Object(id=self.bot.guild_id),
        )

    async def add_reactions_to_message(self, ctx: discord.Interaction, message: discord.Message,):
        await ctx.response.defer(ephemeral=True)

        for emoji in INTEREST_REACTIONS:
            await message.add_reaction(emoji)
            await asyncio.sleep(0.05)

        await ctx.followup.send("Done!", ephemeral=True)

async def setup(bot: Elgatron):
    await bot.add_cog(ReactionCommands(bot), guild=discord.Object(id=bot.guild_id))
