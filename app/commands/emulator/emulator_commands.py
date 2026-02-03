import discord
from discord.ext import commands
from discord import app_commands

from app.core.elgatron import Elgatron
from app.commands.emulator.emulator_model import Emulator
from app.commands.emulator.emulator_view import EmulatorController

class EmulatorCommands(commands.Cog):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot
        # emu = Emulator("./static/game_roms/pokemon_red.gb")  # for debug
        self.emu: Emulator = Emulator("./static/game_roms/pokemon_red.gb", window="null")  # for bot
        self.controller: EmulatorController = EmulatorController(self.emu)

        # make the view work after bot reset
        self.bot.add_view(self.controller)

    async def cog_unload(self):
        self.emu.stop()
        await super().cog_unload()

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
    

async def setup(bot: Elgatron):
    await bot.add_cog(EmulatorCommands(bot), guild=discord.Object(id=bot.guild_id))