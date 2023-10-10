import os
from dotenv import load_dotenv

# Commands from other files
from commands.command_management import * 
from commands.messaging_commands import * 
from commands.epic_games_commands import *
from utilities.settings import guild_id, testing

if testing:
    from commands.test_commands import *


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_id))
    if not testing:
        client.loop.create_task(schedule_post_free_games())
    print("Ready!")


load_dotenv("token.env")
client.run(os.getenv("TOKEN"))
