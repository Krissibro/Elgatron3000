import json

with open("utilities/config.json", "r") as f:
    contents = json.load(f)

guild_id = contents["guild"]
testing = contents["testing"]
