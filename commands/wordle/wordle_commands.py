import discord
from discord import app_commands
from discord.ext import commands

from commands.wordle.Wordle import Wordle
from utilities.elgatron import Elgatron


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
        await ctx.response.send_message(embed= self.wordle.guess_word(ctx, word))

    @app_commands.command(
        name="current",
        description="See the current progress of the daily wordle!",
    )
    async def current_game(self, ctx: discord.Interaction):
        await ctx.response.send_message(embed= self.wordle.make_embed())

    @app_commands.command(
        name="stats",
        description="See the wordle statistics!",
    )
    async def show_stats(self, ctx: discord.Interaction, only_show_to_me: bool = False):
        await ctx.response.send_message(embed=self.wordle.make_stats_embed(), ephemeral=only_show_to_me)

    # @commands.is_owner()
    @app_commands.command(
        name="reset",
        description="Reset the daily wordle",
    )
    async def reset_wordle(self, ctx: discord.Interaction):
        if not await self.bot.is_owner(ctx.user):
            embed = discord.Embed(title="You do not have permission to use this command!",)
            await ctx.response.send_message(
                embed=embed,
                ephemeral=True,
                delete_after=15
            )
            return

        await self.wordle.start_new_game()
        await ctx.response.send_message(embed=discord.Embed(title="Wordle has been reset!"), ephemeral=True, delete_after=10)


async def setup(bot: Elgatron):
    await bot.add_cog(WordleCommands(bot), guild=discord.Object(id=bot.guild_id))



