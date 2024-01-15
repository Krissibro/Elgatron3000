# Shared Imports
import discord
from discord import app_commands
import asyncio
import sqlite3
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import timedelta

from utilities.settings import guild_id

# Shared Variables
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

database = sqlite3.connect('./data/database.db')
cursor = database.cursor()

cursor.execute('''
        DROP TABLE IF EXISTS wordle;
    ''')

cursor.execute('''
        DROP TABLE IF EXISTS wordle_guesses;
    ''')

cursor.execute('''
        CREATE TABLE wordle (
            game DATE       NOT NULL PRIMARY KEY,
            word VARCHAR(5) NOT NULL
        )
    ''')

cursor.execute('''
        CREATE TABLE wordle_guesses (
            ID       INTEGER PRIMARY KEY,
            game     DATE                       NOT NULL,
            guess_nr SMALLINT                   NOT NULL,
            guess    VARCHAR(5)                 NOT NULL,
            person   VARCHAR(20)                NOT NULL,
            FOREIGN KEY (game) references wordle (game)
        )
    ''')
database.commit()

scheduler = AsyncIOScheduler(timezone='Europe/Oslo')
