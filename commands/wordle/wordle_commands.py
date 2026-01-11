import discord
from discord import app_commands
from discord.ext import commands

from apscheduler.triggers.cron import CronTrigger
from pyboy.utils import AccessError

from commands.wordle.wordle_model import WordleModel
from commands.wordle.wordle_stats import WordleStats
from commands.wordle.wordle_view import WordleView
from utilities.elgatron import Elgatron
from utilities.validators import validate_messageable


@app_commands.guild_only()
class WordleCommands(commands.GroupCog, group_name="wordle"):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot
        self.wordle_stats = WordleStats()
        self.wordle_model = WordleModel(self.wordle_stats, testing=bot.testing)
        self.wordle_view: WordleView = WordleView(bot, self.wordle_model, self.wordle_stats, testing=self.bot.testing)
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
        self.wordle_model.guess_word(ctx, word)

        await ctx.response.send_message(embed=self.wordle_view.make_wordle_embed())

    @app_commands.command(
        name="current",
        description="See the current progress of the daily wordle!",
    )
    async def current_game(self, ctx: discord.Interaction):
        await ctx.response.send_message(embed=self.wordle_view.make_wordle_embed())

    @app_commands.command(
        name="stats",
        description="See the wordle statistics!",
    )
    async def show_stats(self, ctx: discord.Interaction, only_show_to_me: bool = False):
        await ctx.response.send_message(embed=self.wordle_view.make_stats_embed(), ephemeral=only_show_to_me)

    # @commands.is_owner()
    @app_commands.command(
        name="reset",
        description="Reset the daily wordle",
    )
    async def reset_wordle(self, ctx: discord.Interaction):
        if not await self.bot.is_owner(ctx.user):
            raise PermissionError("You do not have permission to use this command!")

        await self.start_new_game()
        await ctx.response.send_message(embed=discord.Embed(title="Wordle has been reset!"), ephemeral=True, delete_after=10)

    async def start_new_game(self) -> None:
        channel = validate_messageable(self.bot.get_channel(self.channel_id))
        daily_word = self.wordle_model.daily_word.upper()

        if not self.wordle_model.correct_guess and daily_word:
            await channel.send(embed=self.wordle_view.make_game_over_embed(daily_word))
            self.wordle_stats.reset_streak()

        self.wordle_model.pick_new_word()

        if self.bot.testing:
            print(self.wordle_model.daily_word)
        else:
            await channel.send(embed=self.wordle_view.new_game_embed())

    async def send_wordle_reminder(self) -> None:
        """Send reminder if the daily wordle hasn't been completed"""
        if not self.wordle_model.correct_guess:
            await self.wordle_view.send_reminder()

    async def cog_app_command_error(self, interaction: discord.Interaction, error: Exception):
        await self.bot.handle_command_error(interaction, error)

async def setup(bot: Elgatron):
    await bot.add_cog(WordleCommands(bot), guild=discord.Object(id=bot.guild_id))



