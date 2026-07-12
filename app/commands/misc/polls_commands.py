import asyncio

from datetime import datetime, timedelta
from typing import Dict

import discord
from typing import Optional
from discord import app_commands
from discord.ext import commands

from app.core.elgatron import Elgatron
from app.utilities.transformers import DateTransformer


class PollCommands(commands.GroupCog, group_name="poll"):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot

    @app_commands.command(
        name="custom",
        description="create a custom poll",
    )
    async def start_poll(
        self,
        ctx: discord.Interaction,
        title: str,
        option1: str,
        option2: str,
        description: Optional[str] = None,
        role_mention: Optional[discord.Role] = None,
        option3: Optional[str] = None,
        option4: Optional[str] = None,
        option5: Optional[str] = None,
        option6: Optional[str] = None,
        option7: Optional[str] = None,
        option8: Optional[str] = None,
        option9: Optional[str] = None,
        option10: Optional[str] = None,
    ):
        # Make a list with valid options
        options = [
            option1, option2, option3, option4, option5, option6, option7, option8, option9, option10,
        ]
        options = [
            option for option in options if option
        ]  # remove the options that are undefined
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        option_dict = {}
        for i, j in zip(emojis, options):
            option_dict[i] = j
        await self.make_poll(ctx, option_dict, title, description, role_mention)

    @app_commands.command(
        name="numbers",
        description="create a number poll",
    )
    async def start_numbers(
        self,
        ctx: discord.Interaction,
        title: str,
        options: app_commands.Range[int, 2, 10],
        description: Optional[str] = None,
        role_mention: Optional[discord.Role] = None,
    ):
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        option_dict = {}

        for emoji in emojis[:options]:
            option_dict[emoji] = ""

        await self.make_poll(ctx, option_dict, title, description, role_mention, write_options=False)

    @app_commands.command(
        name="dates",
        description="create a date poll",
    )
    async def start_dates(
        self,
        ctx: discord.Interaction,
        title: str,
        date: app_commands.Transform[datetime, DateTransformer],
        days: app_commands.Range[int, 2, 10],
        description: Optional[str] = None,
        role_mention: Optional[discord.Role] = None,
    ):
        if ctx.response.is_done():
            return

        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        option_dict = {}

        for i in range(days):
            option_dict[emojis[i]] = (date + timedelta(days=i)).strftime("%A %d.%m")

        await self.make_poll(ctx, option_dict, title, description, role_mention)

    @staticmethod
    async def make_poll(
        ctx: discord.Interaction,
        options: Dict[str, str],
        title: str,
        description: Optional[str] = None,
        role_mention: Optional[discord.Role] = None,
        write_options: bool = True,
    ) -> None:
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        embed = discord.Embed(title=title, description=description)
        if write_options:
            content = "\n\n".join([f"{i}  {j}" for i, j in options.items()])
            embed.add_field(name=content, value="", inline=False)

        await ctx.response.send_message(embed=embed)
        msg = await ctx.original_response()

        for emoji in emojis[: len(options)]:
            await msg.add_reaction(emoji)
            await asyncio.sleep(0.05)
        thread = await msg.create_thread(name=title[:100])

        if role_mention is not None:
            await thread.send(content=role_mention.mention + " GET YO ASS IN HERE")


async def setup(bot: Elgatron):
    await bot.add_cog(PollCommands(bot), guild=discord.Object(id=bot.guild_id))
