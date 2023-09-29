import discord

# More commands from other files
from commands.command_management import * 
from commands.messaging_commands import * 
from commands.epic_games_commands import * 



@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=508383744336461842))
    client.loop.create_task(schedule_post_free_games())
    print("Ready!")
    

#client.run("token")
# test bot
client.run("MTE1NTExOTgyNjY1MDUzMzkxOA.GP7imZ.WI0vvGZjr7baUVbBQatop4yTnm1Tb9bniVkTrw")

# Actual bot
# client.run("ODM3Nzg0MTQxNjYzMDQzNjk1.GnFD0Z.DTgQW2gO1-yRnJ3eFQ5-ijOoAT1HTD0NLNvwkY")
