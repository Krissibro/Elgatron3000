import io

import discord

from utilities.shared import tree
from utilities.settings import guild_id
from the_lab.emulator_tests import Emulator
# for debug
emu = Emulator("./the_lab/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb")
# for bot
#emu = Emulator("./the_lab/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb", window="null")


@tree.command(
    name="start_game",
    description="start a poll",
    guild=discord.Object(id=guild_id)
)
async def start_game(ctx):
    await ctx.response.send_message(view=EmulatorController(ctx))


@tree.command(
    name="pass_time",
    description="start a poll",
    guild=discord.Object(id=guild_id)
)
async def pass_time(ctx, time: int):
    await ctx.response.defer()

    for _ in range(time):
        emu.tick()

    with open("emulator.gif", "wb") as file:
        file.write(emu.make_gif().read())

    file = discord.File(fp=emu.make_gif(), filename="emulator.gif")
    await ctx.followup.send(file=file)


class EmulatorController(discord.ui.View):

    def __init__(self, message_ctx):
        super().__init__(timeout=None)
        self.message_ctx = message_ctx

    async def update_gif(self):
        file = discord.File(fp=emu.make_gif(), filename="emulator.gif")

        await self.message_ctx.edit_original_response(attachments=[file], view=self)

    @discord.ui.button(emoji="🅰️", style=discord.ButtonStyle.red, row=0)
    async def A_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        emu.sim_button_time("A", 200)

        await self.update_gif()

    @discord.ui.button(emoji="🔼", style=discord.ButtonStyle.blurple, row=0)
    async def up_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        emu.sim_button_time("up", 200)

        await self.update_gif()

    @discord.ui.button(emoji="🅱️", style=discord.ButtonStyle.red, row=0)
    async def B_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        emu.sim_button_time("B", 200)

        await self.update_gif()

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple, row=1)
    async def left_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        emu.sim_button_time("Left", 200)

        await self.update_gif()

    @discord.ui.button(emoji="🔽", style=discord.ButtonStyle.blurple, row=1)
    async def down_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        emu.sim_button_time("Down", 200)

        await self.update_gif()

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple, row=1)
    async def right_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        emu.sim_button_time("Right", 200)

        await self.update_gif()

    @discord.ui.button(emoji="📃", style=discord.ButtonStyle.grey, row=2)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        emu.sim_button_time("start", 200)

        await self.update_gif()

    @discord.ui.button(emoji="🩶", style=discord.ButtonStyle.grey, row=2, disabled=True)
    async def empty_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(emoji="🔎", style=discord.ButtonStyle.grey, row=2)
    async def select_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        emu.sim_button_time("select", 200)

        await self.update_gif()