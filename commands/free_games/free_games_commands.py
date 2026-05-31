import discord
from discord import app_commands
from discord.ext import commands

from apscheduler.triggers.cron import CronTrigger

from commands.free_games.free_games_model import FreeGameManager
from utilities.elgatron import Elgatron
from utilities.validators import validate_messageable


class EpicGames(commands.Cog):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot
        self.free_games: FreeGameManager = FreeGameManager(self.bot)

        trigger = CronTrigger(hour=18, minute=0, second=0, timezone='Europe/Oslo')
        job_id = "post_free_games"
        if not bot.scheduler.get_job(job_id):
            bot.scheduler.add_job(
                self.free_games.scheduled_post_free_games, trigger=trigger, id=job_id
            )

    @app_commands.command(
        name="free_games_rn",
        description="See the currently free games on Epic Games"
    )
    async def free_games_rn(self, ctx: discord.Interaction):
        await ctx.response.send_message(embed=self.free_games.make_link_embed())

        channel = validate_messageable(ctx.channel)

        self.free_games.update_free_games()
        await self.free_games.send_games_embed(channel)


async def setup(bot: Elgatron):
    await bot.add_cog(EpicGames(bot), guild=discord.Object(id=bot.guild_id))
