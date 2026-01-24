import discord
from discord import app_commands
from discord.ext import commands

from apscheduler.triggers.cron import CronTrigger

from app.commands.wordle.wordle_db import WordleDB
from app.commands.wordle.wordle_view import WordleView

from app.utilities.errors import ElgatronError
from app.core.elgatron import Elgatron
from app.utilities.validators import validate_messageable


@app_commands.guild_only()
class WordleCommands(commands.GroupCog, group_name="wordle_db"):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot
        self.wordle_db = WordleDB(bot.testing)
        self.wordle_view: WordleView = WordleView(bot, self.wordle_db)
        self.channel_id = bot.testing_channel_id if bot.testing else bot.wordle_channel_id

        new_word_trigger = CronTrigger(hour=8, minute=0, second=0, timezone='Europe/Oslo')
        bot.scheduler.add_job(self.start_new_game, new_word_trigger, id="wordle_pick_new_word")

        reminder_trigger = CronTrigger(hour=22, minute=0, second=0, timezone='Europe/Oslo')
        bot.scheduler.add_job(self.send_wordle_reminder, reminder_trigger, id="wordle_reminder")

    @app_commands.command(
        name="guess",
        description="Attempt to guess the daily wordle!",
    )
    async def guess_word(self, ctx: discord.Interaction, word: str) -> None:
        await self.wordle_db.guess_word(word, ctx.user)

        await ctx.response.send_message(embed=await self.wordle_view.make_wordle_embed())

    @app_commands.command(
        name="current",
        description="See the current progress of the daily wordle!",
    )
    async def current_game(self, ctx: discord.Interaction):
        await ctx.response.send_message(embed=await self.wordle_view.make_wordle_embed())

    # @commands.is_owner()
    @app_commands.command(
        name="reset",
        description="Reset the daily wordle",
    )
    async def reset_wordle(self, ctx: discord.Interaction):
        if not await self.bot.is_owner(ctx.user):
            raise ElgatronError("You do not have permission to use this command!")

        await self.start_new_game()
        await ctx.response.send_message(embed=discord.Embed(title="Wordle has been reset!"), ephemeral=True, delete_after=10)

    async def start_new_game(self) -> None:
        game = await self.wordle_db.get_current_game()
        channel = validate_messageable(self.bot.get_channel(self.channel_id))
        daily_word = game.word.upper()

        if not game.finished and daily_word:
            await channel.send(embed=self.wordle_view.make_game_over_embed(daily_word))

        game = await self.wordle_db.new_game()

        if self.bot.testing:
            print(game.word)
        else:
            await channel.send(embed=self.wordle_view.new_game_embed())

    async def send_wordle_reminder(self) -> None:
        """Sends the reminder if the daily wordle hasn't been completed"""
        game = await self.wordle_db.get_current_game()
        if not game.finished:
            await self.wordle_view.send_reminder()


async def setup(bot: Elgatron):
    await bot.add_cog(WordleCommands(bot), guild=discord.Object(id=bot.guild_id))



