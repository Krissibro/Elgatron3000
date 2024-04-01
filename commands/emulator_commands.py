import discord

from utilities.shared import tree
from utilities.settings import guild_id
from command_objects.Emulator import Emulator
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
    await ctx.response.defer()
    for _ in range(1500): #time needed to get to titlescreen
        emu.tick()
    file = discord.File(fp=emu.make_gif(), filename="emulator.gif")
    msg = await ctx.edit_original_response(attachments=[file], view=EmulatorController(ctx))

    await msg.create_thread(name="Discuss Tottoko Hamutarou!")


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

    @discord.ui.button(emoji="⌚", style=discord.ButtonStyle.grey, row=2)
    async def empty_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for _ in range(500):
            emu.tick()

        await self.update_gif()

    @discord.ui.button(emoji="🔎", style=discord.ButtonStyle.grey, row=2)
    async def select_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        emu.sim_button_time("select", 200)

        await self.update_gif()