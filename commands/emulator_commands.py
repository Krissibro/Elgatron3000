import discord

from utilities.settings import guild_id, tree
from command_objects.Emulator import Emulator
from typing import Optional

# for debug
# emu = Emulator("./data/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb")
# for bot
emu = Emulator("./data/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb", window="null")


@tree.command(
    name="pokemon",
    description="Sends controller to play Pokemon!",
    guild=discord.Object(id=guild_id)
)
async def pokemon(ctx: discord.Interaction):
    await ctx.response.defer()
    emu.sim_button_time(None, 1500)
    file = discord.File(fp=emu.make_gif(), filename="emulator.gif")

    msg = await ctx.edit_original_response(attachments=[file], view=EmulatorController())
    await msg.create_thread(name="Discuss Pokemon!")


class EmulatorController(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    async def update_gif(self, interaction: discord.Interaction) -> None:
        file = discord.File(fp=emu.make_gif(), filename="emulator.gif")

        await interaction.response.edit_message(attachments=[file], view=self)

    async def update(self, interaction: discord.Interaction, button: Optional[str], frames: int) -> None:
        emu.sim_button_time(button, frames)

        await self.update_gif(interaction)

    @discord.ui.button(emoji="🅰️", style=discord.ButtonStyle.red, row=0, custom_id="A_Button")
    async def A_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "A", 200)

    @discord.ui.button(emoji="🔼", style=discord.ButtonStyle.blurple, row=0, custom_id="Up_Button")
    async def up_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "up", 200)

    @discord.ui.button(emoji="🅱️", style=discord.ButtonStyle.red, row=0, custom_id="B_Button")
    async def B_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "B", 200)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple, row=1, custom_id="Left_Button")
    async def left_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "left", 200)

    @discord.ui.button(emoji="🔽", style=discord.ButtonStyle.blurple, row=1, custom_id="Down_Button")
    async def down_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "down", 200)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple, row=1, custom_id="Right_Button")
    async def right_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "right", 200)

    @discord.ui.button(emoji="📃", style=discord.ButtonStyle.grey, row=2, custom_id="Select_Button")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "start", 200)

    @discord.ui.button(emoji="⌚", style=discord.ButtonStyle.grey, row=2, custom_id="Wait_Button")
    async def empty_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, None, 200)

    @discord.ui.button(emoji="🔎", style=discord.ButtonStyle.grey, row=2, custom_id="Settings_Button")
    async def select_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.update(interaction, "select", 200)
