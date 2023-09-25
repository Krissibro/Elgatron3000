import discord
from discord import app_commands
from datetime import timedelta
import asyncio
from backend import *

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


running_commands_dict = {}

class Command:
    current_ids = set()
    
    def __init__(self, embed, task):
        self.id = self.assign_id()
        self.embed = embed
        self.process = task
        
    # Assigns the lowest ID
    def assign_id(self):
        i = 1
        while i in Command.current_ids:
            i += 1
        Command.current_ids.add(i)
        return i
    
    def kill(self):
        self.process.cancel()
        Command.current_ids.remove(self.id)



@tree.command(
    name="running_commands",
    description="See the currently running commands",
    guild=discord.Object(id=508383744336461842)
)
async def running_commands(ctx):
    if not running_commands_dict:
        await ctx.response.send_message("No commands running") 
        
    await ctx.response.send_message("Showing all running processes")

    for id, command in running_commands_dict.items():
        embed = command.embed
        await ctx.channel.send(f"ID: {id}", embed = embed)



@tree.command(
    name="kill_command",
    description="Kill a specific running command using an ID",
    guild=discord.Object(id=508383744336461842)
)
async def kill_command(ctx, id: int):
    running_commands_dict[id].kill()
    del running_commands_dict[id]
    await ctx.response.send_message(f"Command {id} has been terminated")



@tree.command(
    name="kill_all_commands",
    description="Kill all running commands",
    guild=discord.Object(id=508383744336461842)
)
async def kill_all_commands(ctx):
    for command in running_commands_dict.values():
        command.kill()
    running_commands_dict.clear()
    embed = discord.Embed(
        title="All running commands have been terminated."
    )
    await ctx.response.send_message(embed = embed)



@tree.command(
    name="cleanup",
    description="Clean the current chat for bot messages",
    guild=discord.Object(id=508383744336461842)
)
async def cleanup(ctx, messages_amount: int):
    await ctx.response.defer()
    await ctx.channel.purge(limit=messages_amount, check=lambda m: m.author == client.user)
    await ctx.channel.send(f"Deleted {messages_amount} messages", delete_after=3)



@tree.command(
    name="dm_aga",
    description="Annoy HA as many times as you would like with a given interval!",
    guild=discord.Object(id=508383744336461842)
)
async def dm_aga(ctx, message: str, amount: int, interval: str):
    interval = eval(interval)

    command = asyncio.create_task(dm_aga_internal(ctx, message, amount, interval, client))

    embed = discord.Embed (
        title= "Command: DM Aga",
        description= f"Message: {message}"
    )
    embed.add_field(name="Amount:", value= f"{amount}", inline=False)
    embed.add_field(name="Interval:", value=f"{timedelta(seconds=interval)}", inline=False)
    
    command_tracker = Command(embed, command)
    running_commands_dict[command_tracker.id] = command_tracker
    await command
    
    del running_commands_dict[command_tracker.id]
    Command.current_ids.remove(command_tracker.id)


@tree.command(
    name="annoy",
    description="Spam a message at someone!",
    guild=discord.Object(id=508383744336461842)
)
async def annoy(ctx, user: str, message: str, amount: int, interval: str):
    interval = eval(interval)

    command = asyncio.create_task(annoy_internal(ctx, user, message, amount, interval))

    embed = discord.Embed (
        title= "Command: Annoy",
        description= f"Message: {message}"
    )
    embed.add_field(name="User:", value=f"{user}", inline=False)
    embed.add_field(name="Amount:", value=f"{amount}", inline=False)
    embed.add_field(name="Interval:", value=f"{timedelta(seconds=interval)}", inline=False)

    command_tracker = Command(embed, command)
    running_commands_dict[command_tracker.id] = command_tracker
    
    await command
    
    del running_commands_dict[command_tracker.id]
    Command.current_ids.remove(command_tracker.id)



@tree.command(
    name="get_attention",
    description="Ping someone x times, once every 60 seconds till they react",
    guild=discord.Object(id=508383744336461842)
)
async def get_attention(ctx, user: str, message: str, amount: int):

    command = asyncio.create_task(get_attention_internal(ctx, user, message, amount, client))

    embed = discord.Embed (
        title= "Command: Annoy",
        description= f"Message: {message}"
    )
    embed.add_field(name="User:", value=f"{user}", inline=False)
    embed.add_field(name="Amount:", value=f"{amount}", inline=False)

    command_tracker = Command(embed, command)
    running_commands_dict[command_tracker.id] = command_tracker
    
    await command
    
    del running_commands_dict[command_tracker.id]
    Command.current_ids.remove(command_tracker.id)
        


@tree.command(
    name="help",
    description="Bot info!",
    guild=discord.Object(id=508383744336461842)
)
async def help(ctx):
    embed = discord.Embed(
        title="📚 Help"
        )
    embed.add_field(name="/annoy", value="<user> <message> <amount> <interval>", inline=False)
    embed.add_field(name="/dm_aga", value="<message> <amount> <interval>", inline=False)
    embed.add_field(name="/get_attention", value="<user> <message> <amount>", inline=False)
    embed.add_field(name="/cleanup", value="<messages_amount>", inline=False)
    embed.set_footer(text="<interval> is in seconds, but can be evaluated by for example 20*60")

    await ctx.response.send_message(embed = embed)



@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=508383744336461842))
    print("Ready!")


#client.run("ODM3Nzg0MTQxNjYzMDQzNjk1.GnFD0Z.DTgQW2gO1-yRnJ3eFQ5-ijOoAT1HTD0NLNvwkY")

#test bot
client.run("MTE1NTExOTgyNjY1MDUzMzkxOA.GP7imZ.WI0vvGZjr7baUVbBQatop4yTnm1Tb9bniVkTrw")
