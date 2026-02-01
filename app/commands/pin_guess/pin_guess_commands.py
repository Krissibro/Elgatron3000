import discord
import io

from discord import app_commands
from discord.ext import commands

from app.core.elgatron import Elgatron

from app.commands.pin_guess.pin_db import PinDB
from app.models.pin_model import Pin
from app.commands.pin_guess.pin_guess_view import PinView, TempPinView

class GuessThatPin(commands.GroupCog, group_name="pin"):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot
        self.pin_db: PinDB = PinDB()

    @app_commands.command(
        name="guess",
        description="Guess the pin!",
    )
    async def guess_that_pin(self, ctx: discord.Interaction):
        pin: Pin = await self.pin_db.load_random_pin()
        view: PinView = PinView(pin)

        if not pin.has_files:
           await ctx.response.send_message(embed=view.make_first_embed(), view=view)
        else:
            # if there are files show preview as soon as possible
            await ctx.response.send_message(embed=view.make_first_embed(), view=TempPinView())
            # then edit with the full view
            await ctx.edit_original_response(view=view, attachments=await self.get_message_attatchments(pin))

    @app_commands.command(
        name="sync",
        description="re-sync pins!",
    )
    async def sync_pins(self, ctx: discord.Interaction) -> None:
        await self.pin_db.fetch_pins(self.bot)

        embed = discord.Embed(title=f"{len(self.pin_db.pins)} pins were loaded!",)
        await ctx.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Detects if a message has been edited, ONLY works for messages sent after the bot started.
        If a message is pinned, it is saved to the storage.
        If a message is unpinned, it is removed from storage"""

        # If pinned
        if not before.pinned and after.pinned:
            await self.pin_db.add_pin(after)

        # If unpinned
        if before.pinned and not after.pinned:
            await self.pin_db.remove_pin(after)

    async def get_message_attatchments(self, pin: Pin) -> list[discord.File]:
        message = await pin._fetch_message(self.bot)
        if message is None:
            return []
        files = []
        for attatchment in message.attachments:
            data = await attatchment.read()
            files.append(discord.File(io.BytesIO(data), attatchment.filename))
        return files


async def setup(bot: Elgatron):
    await bot.add_cog(GuessThatPin(bot), guild=discord.Object(id=bot.guild_id))