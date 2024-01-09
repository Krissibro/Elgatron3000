# Shared Imports
import discord
from discord import app_commands
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import timedelta

from utilities.settings import guild_id

# Shared Variables
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

scheduler = AsyncIOScheduler(timezone='Europe/Oslo')


