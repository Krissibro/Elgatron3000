import discord
import csv

from discord import app_commands
from discord.ext import commands

from utilities.elgatron import Elgatron
from commands.free_games.free_games_commands import FreeGameManager


class TestCommands(commands.GroupCog, group_name="test"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="collect_data",
        description="testing data collection"
    )
    @discord.app_commands.checks.bot_has_permissions(read_message_history=True)
    async def collect_data(self, ctx: discord.Interaction):
        await ctx.response.defer(ephemeral=True)
        messages = []
        for i in ctx.guild.text_channels:
            print(i.name)
            if i.name in ["logs", "fishing-pond"]:
                continue
            try:
                messages.extend([[
                    message.channel,
                    message.author,
                    message.created_at,
                    message.clean_content,
                    [reaction.emoji for reaction in message.reactions],
                    [".".join(attachment.filename.split(".")[0:-1]) for attachment in message.attachments],
                    [attachment.filename.split(".")[1] for attachment in message.attachments],
                    [attachment.content_type for attachment in message.attachments]
                ] async for message in i.history(limit=10)])
            except:  # TODO specify what kind of error can occur here?
                continue
        with open('data/messages.csv', 'w', newline='', encoding='utf-8') as csvfile:
            print("finished!")
            writer = csv.writer(csvfile)
            writer.writerows(messages)

        embed = discord.Embed(title=f"Collected {len(messages)} messages")
        await ctx.edit_original_response(embed=embed)

    @app_commands.command(
        name="test_epic_games_scheduler",
        description="testing"
    )
    async def test_epic_games_scheduler(self, ctx):
        await ctx.response.send_message(embed=discord.Embed(title="Testing!"), ephemeral=True, delete_after=10)
        free_games = FreeGameManager(self.bot)
        await free_games.scheduled_post_free_games()


async def setup(bot: Elgatron):
    await bot.add_cog(TestCommands(bot), guild=discord.Object(id=bot.guild_id))
