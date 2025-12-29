import asyncio

import discord
from discord.ext import commands
from discord import app_commands

from typing import Dict
from utilities.elgatron import Elgatron


class PollCommands(commands.GroupCog, group_name = "poll"):
    @app_commands.command(
        name="custom",
        description="create a custom poll",
    )
    async def start_poll(self, ctx: discord.Interaction, 
                         title: str, 
                         option1: str, 
                         option2: str, 
                         description: discord.Optional[str] = None,
                         role_mention: discord.Optional[discord.Role] = None,
                         option3: discord.Optional[str] = None,
                         option4: discord.Optional[str] = None, 
                         option5: discord.Optional[str] = None,
                         option6: discord.Optional[str] = None, 
                         option7: discord.Optional[str] = None, 
                         option8: discord.Optional[str] = None, 
                         option9: discord.Optional[str] = None,
                         option10: discord.Optional[str] = None):

        # Make list with valid options
        options = [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10]
        options = [option for option in options if option]  # remove option if it's not defined
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        option_dict = {}
        for i, j in zip(emojis, options):
            option_dict[i] = j
        await make_poll(ctx, option_dict, title, description, role_mention)


    @app_commands.command(
        name="numbers",
        description="create a number poll",
    )
    async def start_numbers(self, ctx: discord.Interaction,
                            title: str,
                            options: int,
                            description: discord.Optional[str] = None,
                            role_mention: discord.Optional[discord.Role] = None):
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        option_dict = {}

        for emoji in emojis[:options]:
            option_dict[emoji] = ""

        await make_poll(ctx, option_dict, title, description, role_mention)


async def make_poll(ctx: discord.Interaction, options: Dict[str, str], title: str, description: discord.Optional[str] = None, role_mention: discord.Optional[discord.Role] = None) -> None:
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    embed = discord.Embed(title=title, description=description)
    content = "\n\n".join([f"{i} {j}" for i, j in options.items()])
    embed.add_field(name=content, value="", inline=False)

    await ctx.response.send_message(embed=embed)
    msg = await ctx.original_response()

    for emoji in emojis[:len(options)]:
        await msg.add_reaction(emoji)
        await asyncio.sleep(0.05)
    thread = await msg.create_thread(name=title[:100])

    if role_mention is not None:
        await thread.send(content=role_mention.mention + " GET YO ASS IN HERE")

async def setup(bot: Elgatron):
    await bot.add_cog(PollCommands(bot), guild=discord.Object(id=bot.guild_id))
