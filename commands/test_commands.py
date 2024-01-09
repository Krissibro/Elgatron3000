from utilities.shared import *
from ast import literal_eval


@tree.command(
    name="collect_data",
    description="testing data collection",
    guild=discord.Object(id=guild_id)
)
@app_commands.checks.bot_has_permissions(read_message_history=True)
async def collect_data(ctx: discord.Interaction):
    await ctx.response.defer()
    data = [[message.channel.name, message.author.name, message.clean_content] async for message in ctx.channel.history(limit=200)]
    for i in data:
        print(i) if i[2] else None
