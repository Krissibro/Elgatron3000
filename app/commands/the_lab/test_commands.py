import csv

import discord
from discord import app_commands
from discord.ext import commands

from app.core.elgaTree import ElgatronError
from app.core.elgatron import Elgatron


class TestCommands(commands.GroupCog, group_name="test"):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot

    @app_commands.command(
        name="collect_data",
        description="testing data collection"
    )
    @discord.app_commands.checks.bot_has_permissions(read_message_history=True)
    async def collect_data(self, ctx: discord.Interaction):
        await ctx.response.defer(ephemeral=True)
        messages = []

        if ctx.guild is None:
            raise ElgatronError("There are no text channels (HOW???)")

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
        with open('static/messages.csv', 'w', newline='', encoding='utf-8') as csvfile:
            print("finished!")
            writer = csv.writer(csvfile)
            writer.writerows(messages)

        embed = discord.Embed(title=f"Collected {len(messages)} messages")
        await ctx.edit_original_response(embed=embed)

async def setup(bot: Elgatron):
    await bot.add_cog(TestCommands(bot), guild=discord.Object(id=bot.guild_id))
