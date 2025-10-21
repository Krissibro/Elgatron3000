import discord
from discord.ext import commands
from discord import app_commands

from utilities.settings import guild_id
from commands.emulator.emulator_model import Emulator
from commands.emulator.emulator_view import EmulatorController

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


async def setup(bot):
    await bot.add_cog(EmulatorCommands(bot), guild=bot.get_guild(guild_id))
    print("loaded!")