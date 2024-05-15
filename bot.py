import os
import discord
from dotenv import load_dotenv

# Commands from other files
from commands.command_management import manage_commands, cleanup
from commands.messaging_commands import annoy, get_attention, dm_spam
from commands.polls import start_poll
from commands.epic_games_commands import schedule_post_free_games, free_games_rn
from commands.wordle import initialize_wordle, wordle, guess_wordle
from commands.random_commands import this_dude, weave, pet_elga3, thanos_snapped, trout
from commands.help import help_command
from commands.guess_that_pin import guess_that_pin, initialize_guess_that_pin
from commands.emulator_commands import pokemon, emu

from utilities.settings import guild_id, testing, client, tree

if testing:
    from the_lab.test_commands import *


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_id))

    client.loop.create_task(schedule_post_free_games())
    client.loop.create_task(initialize_wordle())
    client.loop.create_task(initialize_guess_that_pin())

    print("Ready!")


load_dotenv("token.env")
try:
    client.run(os.getenv("TOKEN"))
finally:
    emu.stop()
