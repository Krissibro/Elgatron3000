import discord
from discord.ext import commands
from discord import app_commands

from utilities.settings import guild_id


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Bot info!",
    )
    async def help_command(self, ctx: discord.Interaction):
        embed = discord.Embed(title="📚 Help")
        embed.add_field(name="/annoy",
                        value="Sends a message every given interval", inline=False)

        embed.add_field(name="/dm_spam",
                        value="Sends a direct message to someone every given interval", inline=False)

        embed.add_field(name="/get_attention",
                        value="Mention someone X times, every given interval until they react", inline=False)

        embed.add_field(name="/free_games_rn",
                        value="See free games from Epic Games and Playstation", inline=False)

        embed.add_field(name="/poll start",
                        value="Start a poll with up to 10 options!", inline=False)

        embed.add_field(name="/wordle current",
                        value="Show the current wordle game", inline=False)

        embed.add_field(name="/wordle guess",
                        value="Guess the wordle word", inline=False)

        embed.add_field(name="/wordle stats",
                        value="Shows the server's stats for all played wordle games", inline=False)

        embed.add_field(name="/pokemon",
                        value="Sends pokemon controller and gif",
                        inline=False)

        embed.add_field(name="/cleanup",
                        value="Deletes the given amount of messages", inline=False)

        embed.add_field(name="/manage_commands",
                        value="Manage the running commands, see info and edit/kill running commands", inline=False)

        embed.add_field(name="Funny gifs and videos",
                        value='''/gif trout
                            /gif sus
                            /gif weave
                            /gif this_dude
                            /gif thanos_snapped
                            /gif pet_elga3
                            /gif minecraft''',
                        inline=False)

        embed.set_footer(text='''interval is in the format <XdXhXmXs> 
    Where X is a number and d, h, m, s are days, hours, minutes, seconds respectively''')

        await ctx.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot), guild=bot.get_guild(guild_id))
