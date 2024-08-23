import os
import discord
from dotenv import load_dotenv

# Commands from other files
from commands.command_management import manage_commands, cleanup
from commands.messaging_commands import annoy, get_attention, dm_spam
from commands.polls import start_poll
from commands.epic_games_commands import schedule_post_free_games, free_games_rn
from commands.wordle import *
from commands.random_commands import this_dude, weave, pet_elga3, thanos_snapped, trout
from commands.help import help_command
from commands.guess_that_pin import guess_that_pin, initialize_guess_that_pin
from commands.emulator_commands import pokemon, emu, EmulatorController
from commands.sync import *
from the_lab.petting import petting

from utilities.settings import guild_id, testing, bot, tree

if testing:
    from the_lab.test_commands import *

# TODO: MAY RUN MORE THAN ONCE! :skull:
# TODO: Add more COGS!!!!!
@bot.event
async def on_ready():
    # sync commands
    # await tree.sync(guild=discord.Object(id=guild_id))

    # make emulator buttons work
    bot.add_view(EmulatorController())
    await bot.load_extension("commands.wordle")

    # TODO: Remove these from on_ready
    # initiate scheduled items
    await initialize_guess_that_pin()
    bot.loop.create_task(schedule_post_free_games())

    print("Ready!")


load_dotenv("token.env")
try:
    bot.run(os.getenv("TOKEN"))
finally:
    emu.stop()
