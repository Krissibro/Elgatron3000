from typing import Union

import discord

from discord import app_commands
from discord.ext import commands

from commands.messaging.messaging.messaging_model import execute_command, get_attention_internal, annoy_internal, dm_spam_internal

from utilities.helper_functions import parse_time
from utilities.elgatron import Elgatron


class IntervalTranfsormer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> int:

        result = parse_time(value)
        if result == 0:
            embed = discord.Embed(
                title="Invalid interval format. Please use formats like '10s', '5m5s', '2h30m', etc."
                )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
                )
        return result


# TODO figure out how converters work 
# https://discordpy.readthedocs.io/en/latest/interactions/api.html?highlight=app_commands#transformerss
class MessagingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="dm_spam",
        description="Annoy someone as many times as you would like with a given interval!",
    )
    async def dm_spam(self, ctx, 
                      user: discord.User, 
                      message: str, 
                      amount: discord.app_commands.Range[int, 1, None], 
                      interval: app_commands.Transform[int, IntervalTranfsormer]
                    ):
        if ctx.response.is_done():
            return
        
        await execute_command(ctx, dm_spam_internal, user, message, amount, interval, ctx.channel)

    @app_commands.command(
        name="get_attention",
        description="Ping someone once every 10 seconds 100 times or until they react"
    )
    async def get_attention(self, ctx, 
                            target: Union[discord.User, discord.Role, None], 
                            message: str = "WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP",
                            amount: app_commands.Range[int, 1, None] = 100, 
                            interval: app_commands.Transform[int, IntervalTranfsormer] = 10
                            ):
        if ctx.response.is_done():
            return
        
        await execute_command(ctx, get_attention_internal, target, message, amount, interval, ctx.channel)

    @app_commands.command(
        name="annoy",
        description="Spam a message at someone!",
    )
    async def annoy(self, ctx,
                    message: str,
                    amount: app_commands.Range[int, 1, None],
                    interval: app_commands.Transform[int, IntervalTranfsormer],
                    target: Union[discord.User, discord.Role, None] = None
                    ):
        if ctx.response.is_done():
            return
        
        await execute_command(ctx, annoy_internal, target, message, amount, interval, ctx.channel)


async def setup(bot: Elgatron):
    await bot.add_cog(MessagingCommands(bot), guild=discord.Object(id=bot.guild_id))