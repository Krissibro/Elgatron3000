from utilities.shared import *
from ast import literal_eval
import csv
from commands.wordle import wordle_game

@tree.command(
    name="collect_data",
    description="testing data collection",
    guild=discord.Object(id=guild_id)
)
@app_commands.checks.bot_has_permissions(read_message_history=True)
async def collect_data(ctx: discord.Interaction):
    await ctx.response.defer()
    messages = []
    for i in ctx.guild.text_channels:
        print(i.name)
        if i.name in ["logs", "fishing-pond"]:
            continue
        try:
            messages.extend([[message.created_at.year, message.created_at.month, message.created_at.day, message.created_at.hour] async for message in i.history(limit=100000) if message.author == ctx.user and message.clean_content])
        except:
            continue
    with open('data/messages.csv', 'w', newline='') as csvfile:
        print("finished!")
        writer = csv.writer(csvfile)
        writer.writerows(messages)


@tree.command(
    name="reset_wordle",
    description="Reset the daily wordle",
    guild=discord.Object(id=guild_id)
)
async def reset_wordle(ctx):
    await wordle_game.pick_new_word()
    await ctx.response.defer()
