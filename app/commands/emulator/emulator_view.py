import discord

from typing import Optional

from app.commands.emulator.emulator_model import Emulator

class EmulatorController(discord.ui.View):
    def __init__(self, emu):
        super().__init__(timeout=None)
        self.emu: Emulator = emu

    async def update(self, interaction: discord.Interaction, button: Optional[str], frames: int) -> None:
        # do the emulation
        self.emu.sim_button_time(button, frames)

        # get the GIF and send it
        file = discord.File(fp=self.emu.make_gif(), filename="emulator.gif")
        await interaction.response.edit_message(attachments=[file], view=self)

    @discord.ui.button(emoji="🅰️", style=discord.ButtonStyle.red, row=0, custom_id="A_Button")
    async def a_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "A", 200)

    @discord.ui.button(emoji="🔼", style=discord.ButtonStyle.blurple, row=0, custom_id="Up_Button")
    async def up_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "up", 80)

    @discord.ui.button(emoji="🅱️", style=discord.ButtonStyle.red, row=0, custom_id="B_Button")
    async def b_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
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
