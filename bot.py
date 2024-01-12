import os
from dotenv import load_dotenv

# Commands from other files
from commands.command_management import manage_commands, kill_all_commands, cleanup, help
from commands.messaging_commands import annoy, get_attention, dm_spam
from commands.epic_games_commands import schedule_post_free_games, free_games_rn
from commands.wordle import initialize_wordle, wordle, guess_wordle
from commands.polls import start_poll
from utilities.settings import testing

if testing:
    from commands.test_commands import *


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_id))

    client.loop.create_task(schedule_post_free_games())
    client.loop.create_task(initialize_wordle())

    print("Ready!")


load_dotenv("token.env")
client.run(os.getenv("TOKEN"))
