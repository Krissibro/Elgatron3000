import discord
from discord import app_commands
from discord.ext import commands

from apscheduler.triggers.cron import CronTrigger

from command_objects.Wordle import Wordle
from utilities.settings import testing, scheduler, guild_id


# TODO maybe split this class into 2, a wordle class and a Cog class.
@app_commands.guild_only()
class WordleCommands(commands.GroupCog, group_name="wordle"):
    def __init__(self, bot):
        self.bot = bot
        self.wordle = Wordle(bot)

    @app_commands.command(
        name="guess",
        description="Attempt to guess the daily wordle!",
    )
    async def guess_word(self, ctx: discord.Interaction, word: str) -> None:
        await ctx.response.send_message(embed=await self.wordle.guess_word(ctx, word))

    @app_commands.command(
        name="current",
        description="See the current progress of the daily wordle!",
    )
    async def current_game(self, ctx: discord.Interaction):
        await ctx.response.send_message(embed=await self.wordle.make_embed())

    @app_commands.command(
        name="stats",
        description="See the wordle statistics!",
    )
    async def show_stats(self, ctx: discord.Interaction, only_show_to_me: bool = False):
        await ctx.response.send_message(embed=await self.wordle.make_stats_embed(), ephemeral=only_show_to_me)

    @commands.is_owner()
    @app_commands.command(
        name="reset",
        description="Reset the daily wordle",
    )
    async def reset_wordle(self, ctx: discord.Interaction):
        if not await self.bot.is_owner(ctx.user):
            await ctx.edit_original_response(
                content="You do not have permission to use this command."
            )
            return

        await self.wordle.pick_new_word()
        await ctx.response.send_message(embed=discord.Embed(title="Wordle has been reset!"), ephemeral=True, delete_after=10)


async def setup(bot):
    wordle_cog = WordleCommands(bot)

    await wordle_cog.wordle.load_state()

    job_id = "wordle_pick_new_word"
    if not scheduler.get_job(job_id):
        new_word_trigger = CronTrigger(hour=8, minute=0, second=0, timezone='Europe/Oslo')
        scheduler.add_job(wordle_cog.wordle.pick_new_word, new_word_trigger, id=job_id)
        reminder_trigger = CronTrigger(hour=22, minute=0, second=0, timezone='Europe/Oslo')
        scheduler.add_job(wordle_cog.wordle.send_reminder, reminder_trigger, id="wordle_reminder")

    await bot.add_cog(wordle_cog, guild=bot.get_guild(guild_id))



