import discord

from utils.shared import *



@tree.command(
    name="running_commands",
    description="See the currently running commands",
    guild=discord.Object(id=508383744336461842)
)
async def running_commands(ctx):
    if not running_commands_dict:
        await ctx.response.send_message(embed=discord.Embed(title="No commands running"))
        return

    await ctx.response.send_message(embed=discord.Embed(title="Showing all running processes"))

    for id, command in running_commands_dict.items():
        embed = command.embed
        embed.add_field(name="ID:", value=f"{id}", inline=True)
        await ctx.channel.send(embed=embed)


@tree.command(
    name="kill_command",
    description="Kill a specific running command using an ID",
    guild=discord.Object(id=508383744336461842)
)
async def kill_command(ctx, id: int):
    if id not in running_commands_dict:
        await ctx.response.send_message(embed=discord.Embed(title=f"Command with the ID {id} does not exist"))
        return
    running_commands_dict[id].kill()
    del running_commands_dict[id]
    await ctx.response.send_message(embed=discord.Embed(title=f"Command {id} has been terminated"))


@tree.command(
    name="kill_all_commands",
    description="Kill all running commands",
    guild=discord.Object(id=508383744336461842)
)
async def kill_all_commands(ctx):
    for command in running_commands_dict.values():
        command.kill()
    running_commands_dict.clear()

    await ctx.response.send_message(embed=discord.Embed(title="All running commands have been terminated."))


@tree.command(
    name="cleanup",
    description="Clean the current chat for bot messages",
    guild=discord.Object(id=508383744336461842)
)
async def cleanup(ctx, messages_amount: int):
    await ctx.response.defer()
    await ctx.channel.purge(limit=messages_amount, check=lambda m: m.author == client.user)
    await ctx.channel.send(embed=discord.Embed(title=f"Deleted {messages_amount} messages"), delete_after=3)



@tree.command(
    name="help",
    description="Bot info!",
    guild=discord.Object(id=508383744336461842)
)
async def help(ctx):
    embed = discord.Embed(title="📚 Help")
    embed.add_field(name="/annoy", value="<user> <message> <amount> <interval>", inline=False)
    embed.add_field(name="/dm_aga", value="<message> <amount> <interval>", inline=False)
    embed.add_field(name="/get_attention", value="<user> <message> <amount>", inline=False)
    embed.add_field(name="/free_games_rn", value="See free games from Epic Games", inline=False)
    embed.add_field(name="/cleanup", value="<messages_amount>", inline=False)
    embed.add_field(name="/running_commands", value="See running commands and their IDs", inline=False)
    embed.add_field(name="/kill_command", value="<id>", inline=False)
    embed.add_field(name="/kill_all_commands", value="Kill all commands, try to use /kill_command first", inline=False)
    embed.set_footer(text="<interval> is in seconds, but can be evaluated by for example 20*60")

    await ctx.response.send_message(embed = embed)