import io

import discord

from utilities.shared import tree
from utilities.settings import guild_id
from the_lab.emulator_tests import Emulator

emu = Emulator("./the_lab/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb")


@tree.command(
    name="control",
    description="start a poll",
    guild=discord.Object(id=guild_id)
)
async def control(ctx, command: str):
    if command in ["start", "select", "a", "b", "down", "up", "left", "right"]:
        emu.sim_button_time(command, 120)

        file = discord.File(fp=emu.make_gif(), filename="emulator.gif")
        await ctx.response.send_message(file=file)


@tree.command(
    name="pass_time",
    description="start a poll",
    guild=discord.Object(id=guild_id)
)
async def pass_time(ctx, time: int):
    for _ in range(time):
        emu.tick()

    file = discord.File(fp=emu.make_gif(), filename="emulator.gif")
    await ctx.response.send_message(file=file)
