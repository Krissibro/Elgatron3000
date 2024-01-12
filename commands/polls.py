import discord

from utilities.shared import *
from collections import Counter
from utilities.helper_functions import char_to_emoji


@tree.command(
    name="start_poll",
    description="start a poll",
    guild=discord.Object(id=guild_id)
)
async def start_poll(ctx: discord.Interaction, title: str, option1: str, option2: str, description: str = None,
                     option3: str = None, option4: str = None, option5: str = None, option6: str = None,
                     option7: str = None, option8: str = None, option9: str = None, option10: str = None):

    # sort out options
    options = [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10]
    options = [option for option in options if option]  # remove option if it's not defined

    # make the embed
    embed = discord.Embed(title=title, description=description)
    content = "\n".join([f"{char_to_emoji(i)} {j}" for i, j in enumerate(options)])
    embed.add_field(name=content, value="", inline=False)

    # Send message and add reactions and thread
    await ctx.response.send_message(embed=embed)
    msg = await ctx.original_response()
    for i in range(len(options)):
        await msg.add_reaction(char_to_emoji(i + 1))
    await msg.create_thread(name=title)
