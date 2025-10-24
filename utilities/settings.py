import json

from commands.messaging.ActiveCommands import ActiveCommands
from utilities.elgatron import Elgatron

# TODO deal with most the stuff in here, it should be in the bot i think

active_commands: ActiveCommands = ActiveCommands()

with open("utilities/config.json", "r") as f:
    contents = json.load(f)

guild_id = contents["guild"]
testing = contents["testing"]
game_channel_id = contents["game_channel_id"]
wordle_channel_id = contents["wordle_channel_id"]
testing_channel_id = contents["testing_channel_id"]

bot = Elgatron(guild_id=guild_id, testing=testing)  # Replace with actual guild ID and testing flag