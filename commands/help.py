import discord

from utilities.settings import guild_id, tree


@tree.command(
    name="help",
    description="Bot info!",
    guild=discord.Object(id=guild_id)
)
async def help_command(ctx: discord.Interaction):
    embed = discord.Embed(title="📚 Help")
    embed.add_field(name="/annoy",
                    value="Sends a message every given interval", inline=False)

    embed.add_field(name="/dm_spam",
                    value="Sends a direct message to someone every given interval", inline=False)

    embed.add_field(name="/get_attention",
                    value="Mention someone X times, every given interval until they react", inline=False)

    embed.add_field(name="/free_games_rn",
                    value="See free games from Epic Games and Playstation", inline=False)

    embed.add_field(name="/start_poll",
                    value="Start a poll", inline=False)

    embed.add_field(name="/wordle",
                    value="Show the current wordle game", inline=False)

    embed.add_field(name="/guess_wordle",
                    value="Guess the wordle word", inline=False)

    embed.add_field(name="/pokemon",
                    value="Sends pokemon controller and gif",
                    inline=False)

    embed.add_field(name="/cleanup",
                    value="Deletes the given amount of messages", inline=False)

    embed.add_field(name="/manage_commands",
                    value="Manage the running commands, see info and edit/kill running commands", inline=False)

    embed.add_field(name="Funny gifs and videos",
                    value='''/trout
                        /weave
                        /this_dude
                        /thanos_snapped
                        /pet_elga3''',
                    inline=False)

    embed.set_footer(text='''interval is in the format <XdXhXmXs> 
Where X is a number and d, h, m, s are days, hours, minutes, seconds respectively''')

    await ctx.response.send_message(embed=embed, ephemeral=True)


