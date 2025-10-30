from datetime import datetime, timedelta
from typing import Union

import discord

from discord import app_commands
from discord.ext import commands

from commands.messaging.MessagingInfo import MessagingInfo
from commands.messaging.messaging.messaging_model import get_attention_internal, annoy_internal, dm_spam_internal

from utilities.elgatron import Elgatron
from utilities.transformers import IntervalTranfsormer


class MessagingCommands(commands.Cog):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot

    @app_commands.command(
        name="dm_spam",
        description="Annoy someone as many times as you would like with a given interval!",
    )
    async def dm_spam(self, ctx, 
                      user: discord.User, 
                      message: str, 
                      amount: discord.app_commands.Range[int, 1, None], 
                      interval: app_commands.Transform[timedelta, IntervalTranfsormer]
                    ):
        if ctx.response.is_done():
            return
        
        messaging_info = MessagingInfo(dm_spam_internal, 
                                       user, 
                                       message, 
                                       amount, 
                                       ctx.channel, 
                                       datetime.now() + timedelta(seconds=1),
                                       interval,
                                       self.bot.scheduler
                                       )
        messaging_info.start_job()
        self.bot.active_commands.add_command(messaging_info)
        await ctx.response.send_message(embed=messaging_info.make_embed(), ephemeral=True, delete_after=10)

    @app_commands.command(
        name="get_attention",
        description="Ping someone once every 10 seconds 100 times or until they react"
    )
    async def get_attention(self, ctx, 
                            target: Union[discord.User, discord.Role, None], 
                            message: str = "WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP",
                            amount: app_commands.Range[int, 1, None] = 100, 
                            interval: app_commands.Transform[timedelta, IntervalTranfsormer] = timedelta(seconds=10)
                            ):
        if ctx.response.is_done():
            return
        
        messaging_info = MessagingInfo(get_attention_internal, 
                                       target, 
                                       message, 
                                       amount, 
                                       ctx.channel, 
                                       datetime.now() + timedelta(seconds=1),
                                       interval,
                                       self.bot.scheduler
                                       )
        messaging_info.start_job()
        self.bot.active_commands.add_command(messaging_info)
        await ctx.response.send_message(embed=messaging_info.make_embed(), ephemeral=True, delete_after=10)


    @app_commands.command(
        name="annoy",
        description="Spam a message at someone!",
    )
    async def annoy(self, ctx,
                    message: str,
                    amount: app_commands.Range[int, 1, None],
                    interval: app_commands.Transform[timedelta, IntervalTranfsormer],
                    target: Union[discord.User, discord.Role, None] = None
                    ):
        if ctx.response.is_done():
            return
        
        messaging_info = MessagingInfo(annoy_internal, 
                                       target, 
                                       message, 
                                       amount, 
                                       ctx.channel, 
                                       datetime.now() + timedelta(seconds=1),
                                       interval,
                                       self.bot.scheduler
                                       )
        messaging_info.start_job()
        self.bot.active_commands.add_command(messaging_info)
        await ctx.response.send_message(embed=messaging_info.make_embed(), ephemeral=True, delete_after=10)


async def setup(bot: Elgatron):
    await bot.add_cog(MessagingCommands(bot), guild=discord.Object(id=bot.guild_id))