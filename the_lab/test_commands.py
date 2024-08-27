import discord
import csv

from discord import app_commands
from discord.ext import commands

from utilities.settings import guild_id
from commands.epic_games_commands import scheduled_post_free_games


class TestCommands(commands.GroupCog, group_name="test"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="collect_data",
        description="testing data collection"
    )
    @discord.app_commands.checks.bot_has_permissions(read_message_history=True)
    async def collect_data(self, ctx: discord.Interaction):
        await ctx.response.defer()
        messages = []
        for i in ctx.guild.text_channels:
            print(i.name)
            if i.name in ["logs", "fishing-pond"]:
                continue
            try:
                messages.extend([[message.created_at.year, message.created_at.month, message.created_at.day, message.created_at.hour] async for message in i.history(limit=100000) if message.author == ctx.user and message.clean_content])
            except:  # TODO specify what kind of error can occur here?
                continue
        with open('data/messages.csv', 'w', newline='') as csvfile:
            print("finished!")
            writer = csv.writer(csvfile)
            writer.writerows(messages)

    @app_commands.command(
        name="test_epic_games_scheduler",
        description="testing"
    )
    async def test_epic_games_scheduler(self, ctx):
        await ctx.response.send_message(embed=discord.Embed(title="Testing!"), ephemeral=True, delete_after=10)
        await scheduled_post_free_games()


async def setup(bot):
    await bot.add_cog(TestCommands(bot), guild=bot.get_guild(guild_id))
