import discord
from discord import app_commands
from discord.ext import commands

from apscheduler.triggers.cron import CronTrigger

from app.commands.free_games.free_games_db import FreeGameDB
from app.commands.free_games.free_games_view import FreeGamesView

from app.core.elgatron import Elgatron
from app.utilities.validators import validate_messageable


class EpicGames(commands.Cog):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot
        self.free_games_db: FreeGameDB = FreeGameDB()
        self.free_game_view: FreeGamesView = FreeGamesView()
        self.channel_id = bot.testing_channel_id if bot.testing else bot.game_channel_id

        trigger = CronTrigger(hour=18, minute=0, second=0, timezone='Europe/Oslo')
        bot.scheduler.add_job(self.scheduled_post_free_games, trigger=trigger, id="post_free_games")

    @app_commands.command(
        name="free_games_rn",
        description="See the currently free games on Epic Games"
    )
    async def free_games_rn(self, ctx: discord.Interaction):
        await ctx.response.send_message(embed=self.free_game_view.make_link_embed())
        channel = validate_messageable(ctx.channel)

        await self.free_games_db.update_free_games()

        currently_free_games = await self.free_games_db.get_current_free_games()
        await self.free_game_view.send_games_embeds(currently_free_games, channel)
        
    async def scheduled_post_free_games(self) -> None:
        new_games = await self.free_games_db.update_free_games()
        
        channel = self.bot.get_channel(self.channel_id)
        channel = validate_messageable(channel)

        if new_games:
            await channel.send(embed=self.free_game_view.make_link_embed())
        for game in new_games:
            await channel.send(embed=self.free_game_view.make_game_embed(game))

async def setup(bot: Elgatron):
    await bot.add_cog(EpicGames(bot), guild=discord.Object(id=bot.guild_id))
