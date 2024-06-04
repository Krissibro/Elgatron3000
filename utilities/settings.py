import json
import discord

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Shared Variables
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
scheduler = AsyncIOScheduler(timezone='Europe/Oslo')

with open("utilities/config.json", "r") as f:
    contents = json.load(f)

guild_id = contents["guild"]
testing = contents["testing"]
game_channel_id = contents["game_channel_id"]
wordle_channel_id = contents["wordle_channel_id"]
testing_channel_id = contents["testing_channel_id"]
