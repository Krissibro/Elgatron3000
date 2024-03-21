import os
import discord
from dotenv import load_dotenv

# Commands from other files
from commands.epic_games_commands import schedule_post_free_games
from commands.wordle import initialize_wordle
from commands.guess_that_pin import initialize_guess_that_pin
from commands.emulator import pass_time, start_game

from utilities.shared import client, tree
from utilities.settings import guild_id



@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_id))

    client.loop.create_task(schedule_post_free_games())
    client.loop.create_task(initialize_wordle())
    client.loop.create_task(initialize_guess_that_pin())

    print("Ready!")


load_dotenv("token.env")
client.run(os.getenv("TOKEN"))
