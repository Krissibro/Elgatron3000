import discord
from discord import app_commands
from discord.ext import commands

from apscheduler.triggers.cron import CronTrigger

from app.commands.wordle.wordle_db import WordleDB
from app.commands.wordle.wordle_view import WordleView, WordleFinishedController

from app.utilities.errors import ElgatronError
from app.core.elgatron import Elgatron
from app.utilities.validators import validate_messageable


@app_commands.guild_only()
class WordleCommands(commands.GroupCog, group_name="wordle"):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot
        self.channel_id = bot.testing_channel_id if bot.testing else bot.wordle_channel_id
        
        self.wordle_db = WordleDB(bot.testing)
        self.wordle_view: WordleView = WordleView(bot, self.wordle_db)

        new_word_trigger = CronTrigger(hour=8, minute=0, second=0, timezone='Europe/Oslo')
        bot.scheduler.add_job(self.scheduled_new_game, new_word_trigger, id="wordle_pick_new_word")

        reminder_trigger = CronTrigger(hour=22, minute=0, second=0, timezone='Europe/Oslo')
        bot.scheduler.add_job(self.send_wordle_reminder, reminder_trigger, id="wordle_reminder")

    @app_commands.command(
        name="guess",
        description="Attempt to guess the daily wordle!",
    )
    async def guess_word(self, ctx: discord.Interaction, word: str) -> None:
        if ctx.guild is None:
            raise ElgatronError("This command can only be used in a server.")
        
        await self.wordle_db.guess_word(word, ctx.user)
        
        game = await self.wordle_db.get_current_game()
        embed = await self.wordle_view.make_wordle_embed(game)

        if game.is_finished():
            await ctx.response.send_message(embed=embed, view=WordleFinishedController(game, self.wordle_view))            
            await self.wordle_db.handle_win(ctx.guild.id, game)
        else:
            await ctx.response.send_message(embed=embed)

    @app_commands.command(
        name="current",
        description="See the current progress of the daily wordle!",
    )
    async def current_game(self, ctx: discord.Interaction) -> None:
        game = await self.wordle_db.get_current_game()
        embed = await self.wordle_view.make_wordle_embed(game)

        if game.is_finished():
            await ctx.response.send_message(embed=embed, view=WordleFinishedController(game, self.wordle_view))
        else:
            await ctx.response.send_message(embed=embed)

    @app_commands.command(
        name="stats",
        description="View Wordle statistics for this server",
    )
    async def wordle_stats(self, ctx: discord.Interaction) -> None:
        if ctx.guild is None:
            raise ElgatronError("This command can only be used in a server.")

        stats = await self.wordle_db.get_wordle_stats(ctx.guild.id)
        embed = self.wordle_view.make_stats_embed(stats)

        await ctx.response.send_message(embed=embed)    

    @app_commands.command(
        name="recalculate_stats",
        description="Recalculate Wordle statistics for this server",
    )
    async def recalculate_wordle_stats(self, ctx: discord.Interaction) -> None:
        if not await self.bot.is_owner(ctx.user):
            raise ElgatronError("You do not have permission to use this command!")
        if ctx.guild is None:
            raise ElgatronError("This command can only be used in a server.")

        await ctx.response.defer(thinking=True, ephemeral=True)
        await self.wordle_db.recalculate_stats(ctx.guild.id)
        await ctx.edit_original_response(embed=discord.Embed(title="Wordle statistics recalculated!"))

    @app_commands.command(
        name="reset",
        description="Reset the daily wordle",
    )
    async def reset_wordle(self, ctx: discord.Interaction) -> None:
        if not await self.bot.is_owner(ctx.user) and not self.bot.testing:
            raise ElgatronError("You do not have permission to use this command!")
        if ctx.guild is None:
            raise ElgatronError("This command can only be used in a server.")
        game = await self.wordle_db.get_current_game()

        if not game.is_finished():
            await self.wordle_db.handle_loss(ctx.guild.id, game)
        
        game = await self.wordle_db.new_game()
        self.bot.logger.info(f"Wordle reset by {ctx.user} ({ctx.user.id}). Word is: {game.word}")

        await ctx.response.send_message(embed=discord.Embed(title="Wordle has been reset!"), ephemeral=True, delete_after=10)

    async def scheduled_new_game(self) -> None:
        game = await self.wordle_db.get_current_game()
        channel = validate_messageable(self.bot.get_channel(self.channel_id))

        if not game.is_finished():
            server = self.bot.get_guild(self.bot.guild_id)
            if server is None:
                raise ElgatronError("Guild not found")

            await self.wordle_db.handle_loss(server.id, game)
            embed = self.wordle_view.make_game_over_embed(game.word)
            await channel.send(embed=embed)

        await self.wordle_db.new_game()
        await channel.send(embed=self.wordle_view.new_game_embed())

    async def send_wordle_reminder(self) -> None:
        """Sends the reminder if the daily wordle hasn't been completed"""
        game = await self.wordle_db.get_current_game()
        if not game.is_finished():
            await self.wordle_view.send_reminder()


async def setup(bot: Elgatron):
    await bot.add_cog(WordleCommands(bot), guild=discord.Object(id=bot.guild_id))



