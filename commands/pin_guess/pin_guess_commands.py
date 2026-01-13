import discord

from discord import app_commands
from discord.ext import commands

from utilities.elgatron import Elgatron

from commands.pin_guess.pin_guess_model import PinManager, Pin
from commands.pin_guess.pin_guess_view import PinView, TempPinView

class GuessThatPin(commands.GroupCog, group_name="pin"):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot
        self.pin_manager: PinManager = PinManager()

    @app_commands.command(
        name="guess",
        description="Guess the pin!",
    )
    async def guess_that_pin(self, ctx: discord.Interaction):
        if not self.pin_manager.pins:
            await ctx.response.send_message("No pinned messages found.")
            return

        pin: Pin = await self.pin_manager.load_random_pin()
        view: PinView = PinView(pin)

        # show this as soon as possible
        await ctx.response.send_message(embed=view.make_first_embed(), view=TempPinView())

        # once the rest of the stuff has loaded, show it
        await pin.load_message(self.bot)
        view.original_message = await ctx.edit_original_response(view=view, attachments=pin.build_files())

    @app_commands.command(
        name="sync",
        description="re-sync pins!",
    )
    async def sync_pins(self, ctx: discord.Interaction):
        await self.pin_manager.fetch_pins(self.bot)

        embed = discord.Embed(title=f"{len(self.pin_manager.pins)} pins were loaded!",)
        await ctx.response.send_message(embed=embed)

    @commands.Cog.listener('on_message_edit')
    async def on_message_edit(self, before, after):
        """Detects if a message has been edited.
        If a message is pinned, it is saved to the storage.
        If a message is unpinned, it is removed from storage"""

        # If pinned
        if not before.pinned and after.pinned:
            self.pin_manager.add_pin(after)

        # If unpinned
        if before.pinned and not after.pinned:
            self.pin_manager.remove_pin(after)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: Exception):
        await self.bot.handle_command_error(interaction, error)


async def setup(bot: Elgatron):
    await bot.add_cog(GuessThatPin(bot), guild=discord.Object(id=bot.guild_id))