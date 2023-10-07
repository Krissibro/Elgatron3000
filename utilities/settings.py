import json

with open("utilities/settings.json", "r") as f:
    contents = json.load(f)

guild_id = contents["guild"]
