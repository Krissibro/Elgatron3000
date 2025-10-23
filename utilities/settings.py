import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from commands.messaging.ActiveCommands import ActiveCommands

active_commands: ActiveCommands = ActiveCommands()

with open("utilities/config.json", "r") as f:
    contents = json.load(f)

guild_id = contents["guild"]
testing = contents["testing"]
game_channel_id = contents["game_channel_id"]
wordle_channel_id = contents["wordle_channel_id"]
testing_channel_id = contents["testing_channel_id"]