import os
from dotenv import load_dotenv

# Commands from other files
from commands.command_management import manage_commands, kill_all_commands, cleanup
from commands.messaging_commands import annoy, get_attention, dm_spam
from commands.polls import start_poll
from commands.epic_games_commands import schedule_post_free_games, free_games_rn
from commands.wordle import initialize_wordle, wordle, guess_wordle
from commands.random import *
from commands.help import help_command

from utilities.settings import testing
from utilities.shared import *

if testing:
    from commands.test_commands import collect_data


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_id))

    client.loop.create_task(schedule_post_free_games())
    client.loop.create_task(initialize_wordle())

    print("Ready!")


load_dotenv("token.env")
client.run(os.getenv("TOKEN"))
