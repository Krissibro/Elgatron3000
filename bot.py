import os
import discord
from dotenv import load_dotenv

# Commands from other files
from commands.epic_games_commands import schedule_post_free_games, free_games_rn
from commands.wordle import *
from commands.guess_that_pin import guess_that_pin, initialize_guess_that_pin
from commands.sync import *

from utilities.settings import guild_id, testing, bot, tree

if testing:
    from the_lab.test_commands import *
    from the_lab.petting import petting


# TODO: MAY RUN MORE THAN ONCE! :skull:
# TODO: Add more COGS!!!!!
@bot.event
async def on_ready():
    # sync commands
    # await tree.sync(guild=discord.Object(id=guild_id))

    # make emulator buttons work
    await bot.load_extension("commands.wordle")
    await bot.load_extension("commands.random_commands")
    await bot.load_extension("commands.polls")
    await bot.load_extension("commands.help")
    await bot.load_extension("commands.emulator_commands")
    await bot.load_extension("commands.command_management")
    await bot.load_extension("commands.messaging_commands")

    # TODO: Remove these from on_ready
    # initiate scheduled items
    await initialize_guess_that_pin()
    bot.loop.create_task(schedule_post_free_games())

    print("Ready!")


load_dotenv("token.env")
bot.run(os.getenv("TOKEN"))
