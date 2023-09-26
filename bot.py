import discord
from discord import app_commands
from datetime import timedelta
import asyncio
from backend import *
from epicstore_api import EpicGamesStoreAPI
from datetime import datetime, timedelta, time

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
        await ctx.response.send_message(embed = discord.Embed(title="No commands running"))
        return
        
    await ctx.response.send_message(embed = discord.Embed(title="Showing all running processes"))

    for id, command in running_commands_dict.items():
        embed = command.embed
        embed.add_field(name="ID:", value=f"{id}", inline = True)
        await ctx.channel.send(embed = embed)



@tree.command(
    name="kill_command",
    description="Kill a specific running command using an ID",
    guild=discord.Object(id=508383744336461842)
)
async def kill_command(ctx, id: int):
    if id not in running_commands_dict:
        await ctx.response.send_message(embed = discord.Embed(title=f"Command with the ID {id} does not exist"))
        return
    running_commands_dict[id].kill()
    del running_commands_dict[id]
    await ctx.response.send_message(embed = discord.Embed(title=f"Command {id} has been terminated"))



@tree.command(
    name="kill_all_commands",
    description="Kill all running commands",
    guild=discord.Object(id=508383744336461842)
)
async def kill_all_commands(ctx):
    for command in running_commands_dict.values():
        command.kill()
    running_commands_dict.clear()
    
    await ctx.response.send_message(embed = discord.Embed(title="All running commands have been terminated."))



@tree.command(
    name="cleanup",
    description="Clean the current chat for bot messages",
    guild=discord.Object(id=508383744336461842)
)
async def cleanup(ctx, messages_amount: int):
    await ctx.response.defer()
    await ctx.channel.purge(limit=messages_amount, check=lambda m: m.author == client.user)
    await ctx.channel.send(embed = discord.Embed(title=f"Deleted {messages_amount} messages"), delete_after=3)



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
    name="free_games_rn",
    description="See the currently free games on Epic Games",
    guild=discord.Object(id=508383744336461842)
)
async def free_games_rn(ctx):
    
    title_embed = discord.Embed(title="Free and Epic Games INCOMING!!!!", description="https://store.epicgames.com/en-US/free-games")
    await ctx.response.send_message(embed = title_embed)
    
    await post_free_games(ctx.channel)
    
     
    
             
async def post_free_games(channel):    
    api = EpicGamesStoreAPI()
    free_games = api.get_free_games()["data"]["Catalog"]["searchStore"]["elements"]
    
    for game in free_games:
        effective_date = datetime.fromisoformat(game["effectiveDate"][:-1])
        current_datetime = datetime.utcnow()
        seven_days_ago = current_datetime - timedelta(days=7)
        if effective_date < current_datetime and not effective_date < seven_days_ago:
            embed = discord.Embed(title=game["title"], description=game["description"])
            
            for image in game["keyImages"]:
                if image["type"] == "Thumbnail":
                    embed.set_image(url=image["url"])
            
            await channel.send(embed = embed)   
        
        

async def schedule_post_free_games():
    while True:
        now = datetime.utcnow()
        next_friday = now + timedelta((4-now.weekday()) % 7)  # 4 represents Friday
        next_run = datetime.combine(next_friday.date(), time(18, 0))  # 18:00 UTC
        print(next_run)
        
        # If it's already past Friday 18:00, schedule for the next Friday
        if now >= next_run:  
            next_run += timedelta(weeks=1)
        
        seconds_until_next_run = (next_run - now).total_seconds()
        print(seconds_until_next_run)
        await asyncio.sleep(seconds_until_next_run)
        
        
        channel = client.get_channel(1111353625638350893)
        title_embed = discord.Embed(title="Free and Epic Games INCOMING!!!!", description="https://store.epicgames.com/en-US/free-games")
        await channel.send(embed=title_embed)
        await post_free_games(channel)


# @tree.command(
#     name="test",
#     description="Fuck you!!!!",
#     guild=discord.Object(id=508383744336461842)
# )
# async def test(ctx):
#     await ctx.response.send_message("test")
#     channel = client.get_channel(1111353625638350893)
#     await channel.send("gaming")
    


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
    
    


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=508383744336461842))
    client.loop.create_task(schedule_post_free_games())
    print("Ready!")
    

#test bot
client.run("MTE1NTExOTgyNjY1MDUzMzkxOA.GP7imZ.WI0vvGZjr7baUVbBQatop4yTnm1Tb9bniVkTrw")

# Actual bot
#client.run("ODM3Nzg0MTQxNjYzMDQzNjk1.GnFD0Z.DTgQW2gO1-yRnJ3eFQ5-ijOoAT1HTD0NLNvwkY")
