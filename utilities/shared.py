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


