import json

with open("utilities/config.json", "r") as f:
    contents = json.load(f)

guild_id = contents["guild"]
testing = contents["testing"]
game_channel_id = contents["game_channel_id"]
wordle_channel_id = contents["wordle_channel_id"]
testing_channel_id = contents["testing_channel_id"]
