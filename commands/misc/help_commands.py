import discord
from discord.ext import commands
from discord import app_commands

from utilities.elgatron import Elgatron


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Bot info!",
    )
    async def help_command(self, ctx: discord.Interaction):
        embed = discord.Embed(title="📚 Help")

        # Messaging Group
        embed.add_field(name="**Messaging Commands**",
                        value='''`/annoy` - Spam a message at someone
`/dm_spam` - Annoy someone in their DMs with a given interval
`/get_attention` - Ping someone until they react
`/manage_commands` - See and manage running commands
`/cleanup` - Clean the current chat for bot messages''',
                        inline=False)

        # Poll Group
        embed.add_field(name="**Poll Commands**",
                        value='''`/poll custom` - Create a custom poll with up to 10 options
`/poll numbers` - Create a number poll
`/poll dates` - Create a date poll''',
                        inline=False)

        # Wordle Group
        embed.add_field(name="**Wordle Commands**",
                        value='''`/wordle current` - Show the current wordle game
`/wordle guess` - Guess the wordle word
`/wordle stats` - Shows the server's stats for all played wordle games''',
                        inline=False)

        # Pin Group
        embed.add_field(name="**Pin Commands**",
                        value='''`/pin guess` - Guess which one of your friends pinned a message!
`/pin sync` - Re-sync pinned messages''',
                        inline=False)

        # Stim Group
        embed.add_field(name="**Stim Commands**",
                        value='''`/stim trout` `/stim sus` `/stim weave`
`/stim this_dude` `/stim thanos_snapped`
`/stim pet_elga3` `/stim minecraft` `/stim help`
`/stim wassup_beijing` `/stim gn_girl`
`/stim dr_peppa` `/stim horse`''',
                        inline=False)

        # Standalone Commands
        embed.add_field(name="**Other Commands**",
                        value='''`/free_games_rn` - See currently free games on Epic Games
`/pokemon` - Play Pokemon with an interactive controller
`/petting` - Give people pets!''',
                        inline=False)

        await ctx.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: Elgatron):
    await bot.add_cog(Help(bot), guild=discord.Object(id=bot.guild_id))
