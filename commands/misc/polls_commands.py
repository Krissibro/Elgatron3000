import asyncio

import discord
from discord.ext import commands
from discord import app_commands

from bot import Elgatron


class PollCommands(commands.GroupCog, group_name = "poll"):
    @app_commands.command(
        name="start",
        description="start a poll",
    )
    async def start_poll(self, ctx: discord.Interaction, title: str, option1: str, option2: str, description: str = None,
                         role_mention: discord.Role = None, option3: str = None, option4: str = None, option5: str = None,
                         option6: str = None, option7: str = None, option8: str = None, option9: str = None,
                         option10: str = None):

        # Make list with valid options
        options = [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10]
        options = [option for option in options if option]  # remove option if it's not defined
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        # Make the embed
        embed = discord.Embed(title=title, description=description)
        content = "\n\n".join([f"{i} {j}" for i, j in zip(emojis, options)])
        embed.add_field(name=content, value="", inline=False)

        # Send message and add reactions and thread
        await ctx.response.send_message(embed=embed)
        msg = await ctx.original_response()
        for i in range(len(options)):
            await msg.add_reaction(emojis[i])
            await asyncio.sleep(0.05)
        thread = await msg.create_thread(name=title[:100])

        if role_mention is not None:
            await thread.send(content=role_mention.mention + " GET YO ASS IN HERE")


async def setup(bot: Elgatron):
    await bot.add_cog(PollCommands(bot), guild=discord.Object(id=bot.guild_id))
