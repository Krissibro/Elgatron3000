import discord

from utilities.shared import tree
from utilities.settings import guild_id
from command_objects.Emulator import Emulator
from typing import Optional

# for debug
# emu = Emulator("./data/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb")
# for bot
emu = Emulator("./data/Tottoko Hamutarou 2 - Hamu-chan Zu Daishuugou Dechu (J) [C][!].gbc", window="null")


@tree.command(
    name="tottoko_hamutarou",
    description="Sends controller to play Tottoko Hamutarou!",
    guild=discord.Object(id=guild_id)
)
async def pokemon(ctx):
    # TODO i think some of this can be refactored to the update() func
    await ctx.response.defer()
    for _ in range(1500//emu.skipped_frames): #time needed to get to titlescreen
        emu.tick()
    file = discord.File(fp=emu.make_gif(), filename="emulator.gif")
    msg = await ctx.edit_original_response(attachments=[file], view=EmulatorController())

    await msg.create_thread(name="Discuss Tottoko Hamutarou!")


class EmulatorController(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    async def update_gif(self, interaction: discord.Interaction):
        file = discord.File(fp=emu.make_gif(), filename="emulator.gif")

        await interaction.response.edit_message(attachments=[file], view=self)

    async def update(self, interaction: discord.Interaction, button: Optional[str], frames: int):
        emu.sim_button_time(button, frames)

        await self.update_gif(interaction)

    @discord.ui.button(emoji="🅰️", style=discord.ButtonStyle.red, row=0)
    async def A_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, "A", 200)

    @discord.ui.button(emoji="🔼", style=discord.ButtonStyle.blurple, row=0)
    async def up_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, "up", 200)

    @discord.ui.button(emoji="🅱️", style=discord.ButtonStyle.red, row=0)
    async def B_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, "B", 200)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple, row=1)
    async def left_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, "left", 200)

    @discord.ui.button(emoji="🔽", style=discord.ButtonStyle.blurple, row=1)
    async def down_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, "down", 200)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple, row=1)
    async def right_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, "right", 200)

    @discord.ui.button(emoji="📃", style=discord.ButtonStyle.grey, row=2)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, "start", 200)

    @discord.ui.button(emoji="⌚", style=discord.ButtonStyle.grey, row=2)
    async def empty_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, None, 200)

    @discord.ui.button(emoji="🔎", style=discord.ButtonStyle.grey, row=2)
    async def select_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, "select", 200)
