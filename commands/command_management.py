from utilities.shared import *
from ast import literal_eval


class EditWindow(discord.ui.Modal):
    def __init__(self, old_message:str, old_amount:int, old_interval:int):
        super().__init__(title="Edit")
        self.add_item(discord.ui.TextInput(label="Message:",
                                           style=discord.TextStyle.short,
                                           default=old_message))
        self.add_item(discord.ui.TextInput(label="Amount:",
                                           style=discord.TextStyle.short,
                                           default=old_amount))
        self.add_item(discord.ui.TextInput(label="Interval:",
                                           style=discord.TextStyle.short,
                                           default=old_interval))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()


class SimpleView(discord.ui.View):
    def __init__(self, id: int, running_commands_dict: dict):
        super().__init__()
        self.id= id
        self.command = running_commands_dict[self.id]
    
    @discord.ui.button(emoji="🪦", style=discord.ButtonStyle.red)
    async def kill(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=discord.Embed(title=f"Command {self.id} Killed"), ephemeral=True)
        # ChatGPT made this, idk how it works
        await asyncio.gather(*[i.delete() for i in self.command.info.messages])
        self.command.kill()
        del self.command

        self.stop()

    @discord.ui.button(emoji="🪶", style=discord.ButtonStyle.green)
    async def text_box(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal: discord.ui.Modal = EditWindow(self.command.info.message, self.command.info.remaining, self.command.info.interval)
        await interaction.response.send_modal(modal)
        
        while not modal.is_finished():
            await asyncio.sleep(1)
        self.command.info.message = modal.children[0]
        self.command.info.amount = literal_eval(str(modal.children[1]))
        self.command.info.remaining = literal_eval(str(modal.children[2]))
        self.command.info.interval = literal_eval(str(modal.children[2]))

class DeleteButton(discord.ui.View):
    def __init__(self, messages):
        super().__init__()
        self.messages = messages
    
    @discord.ui.button(emoji="🗑️", style=discord.ButtonStyle.green)
    async def text_box(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await asyncio.gather(*[i.delete() for i in self.messages])
        self.stop()

@tree.command(
    name="manage_commands",
    description="See and manage running commands",
    guild=discord.Object(id=guild_id)
)
async def manage_commands(ctx):
    if not running_commands_dict:
        await ctx.response.send_message(embed=discord.Embed(title="No commands running"), ephemeral=True)
        return

    messages = []

    for id, command in running_commands_dict.items():
        embed = command.get_embed()
        message = await ctx.channel.send(embed=embed, 
                                          view=SimpleView(id, running_commands_dict))
        messages.append(message)

    # TODO: i want this to be ephimeral, but i also want it to be visible to everyone, hmmmmm
    await ctx.response.send_message(embed=discord.Embed(title="Showing all running processes"),
                                     view=DeleteButton(messages))

@tree.command(
    name="kill_command",
    description="Kill a specific running command using an ID",
    guild=discord.Object(id=guild_id)
)
async def kill_command(ctx, id: int):
    if id not in running_commands_dict:
        await ctx.response.send_message(embed=discord.Embed(title=f"Command with the ID {id} does not exist"), ephemeral=True)
        return
    
    running_commands_dict[id].kill()
    del running_commands_dict[id]
    await ctx.response.send_message(embed=discord.Embed(title=f"Command {id} has been terminated"), ephemeral=True)


@tree.command(
    name="kill_all_commands",
    description="Kill all running commands",
    guild=discord.Object(id=guild_id)
)
async def kill_all_commands(ctx):
    for command in running_commands_dict.values():
        command.kill()
    running_commands_dict.clear()

    await ctx.response.send_message(embed=discord.Embed(title="All running commands have been terminated."), ephemeral=True)


@tree.command(
    name="cleanup",
    description="Clean the current chat for bot messages",
    guild=discord.Object(id=guild_id)
)
async def cleanup(ctx, messages_amount: int):
    if messages_amount <= 0:
        await ctx.response.send_message(embed=discord.Embed(title=f"Cannot delete less than 1 message"), ephemeral=True)
        return
    await ctx.response.defer()
    await ctx.channel.purge(limit=messages_amount, check=lambda m: m.author == client.user)
    await ctx.response.send_message(embed=discord.Embed(title=f"Deleted {messages_amount} messages"), ephemeral=True)


@tree.command(
    name="help",
    description="Bot info!",
    guild=discord.Object(id=guild_id)
)
async def help(ctx):
    embed = discord.Embed(title="📚 Help")
    embed.add_field(name="/annoy <message> <amount> <interval> (<user>)", 
                    value="Sends a message every given interval", inline=False)
    embed.add_field(name="/dm_aga <message> <amount> <interval>", 
                    value="Sends a message to HA every given interval", inline=False)
    embed.add_field(name="/get_attention <message> <amount> <interval> <user>", 
                    value="Mention someone X times, every given interval until they react", inline=False)
    embed.add_field(name="/free_games_rn", 
                    value="See free games from Epic Games and Playstation", inline=False)
    embed.add_field(name="/cleanup <messages_amount>", 
                    value="Deletes the given amount of messages", inline=False)
    embed.add_field(name="/manage_commands", 
                    value="Manage and see info about running commands", inline=False)
    embed.add_field(name="/kill_command <ID>", 
                    value="Kills the command with the corresponding ID", inline=False)
    embed.add_field(name="/kill_all_commands", 
                    value="Kill all commands, try to use /kill_command first", inline=False)
    embed.set_footer(text="<interval> is in seconds, but can be evaluated by for example 20*60")

    await ctx.response.send_message(embed=embed, ephemeral=True)
