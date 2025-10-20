import discord
from discord.ext import commands
from discord import app_commands

from utilities.settings import guild_id
from command_objects.Emulator import Emulator
from typing import Optional

class EmulatorCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # emu = Emulator("./data/pokemon_red.gb")  # for debug
        self.emu = Emulator("./data/pokemon_red.gb", window="null")  # for bot
        self.controller = EmulatorController(self.emu)

        # make view work after bot reset
        self.bot.add_view(self.controller)

    def __del__(self):
        self.emu.stop()

    @app_commands.command(
        name="pokemon",
        description="Sends controller to play Pokemon!"
    )
    async def pokemon(self, ctx: discord.Interaction):
        await ctx.response.defer()
        
        self.emu.sim_button_time(None, 1500)
        file = discord.File(fp=self.emu.make_gif(), filename="emulator.gif")

        msg = await ctx.edit_original_response(attachments=[file], view=self.controller)
        await msg.create_thread(name="Discuss Pokemon!")


class EmulatorController(discord.ui.View):

    def __init__(self, emu):
        super().__init__(timeout=None)
        self.emu = emu

    async def update(self, interaction: discord.Interaction, button: Optional[str], frames: int) -> None:
        # do the emulation
        self.emu.sim_button_time(button, frames)

        # get the gif and send it
        file = discord.File(fp=self.emu.make_gif(), filename="emulator.gif")
        await interaction.response.edit_message(attachments=[file], view=self)

    @discord.ui.button(emoji="🅰️", style=discord.ButtonStyle.red, row=0, custom_id="A_Button")
    async def A_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "A", 200)

    @discord.ui.button(emoji="🔼", style=discord.ButtonStyle.blurple, row=0, custom_id="Up_Button")
    async def up_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "up", 80)

    @discord.ui.button(emoji="🅱️", style=discord.ButtonStyle.red, row=0, custom_id="B_Button")
    async def B_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "B", 200)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple, row=1, custom_id="Left_Button")
    async def left_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "left", 80)

    @discord.ui.button(emoji="🔽", style=discord.ButtonStyle.blurple, row=1, custom_id="Down_Button")
    async def down_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "down", 80)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple, row=1, custom_id="Right_Button")
    async def right_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "right", 80)

    @discord.ui.button(emoji="📃", style=discord.ButtonStyle.grey, row=2, custom_id="Select_Button")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "start", 50)

    @discord.ui.button(emoji="⌚", style=discord.ButtonStyle.grey, row=2, custom_id="Wait_Button")
    async def empty_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, None, 300)

    @discord.ui.button(emoji="🔎", style=discord.ButtonStyle.grey, row=2, custom_id="Settings_Button")
    async def select_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "select", 50)


async def setup(bot):
    await bot.add_cog(EmulatorCommands(bot), guild=bot.get_guild(guild_id))