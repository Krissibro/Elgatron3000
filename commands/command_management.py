from utilities.shared import *


class EditWindow(discord.ui.Modal):
    def __init__(self, old_message:str):
        super().__init__(title="Edit")
        self.add_item(discord.ui.TextInput(label="please enter the edit you want to make",
                                           style=discord.TextStyle.short,
                                           default=old_message))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()


class SimpleView(discord.ui.View):
    def __init__(self, id: int, running_commands_dict: dict):
        super().__init__()
        self.id= id
        self.running_commands_dict = running_commands_dict
    
    @discord.ui.button(emoji="🪦", style=discord.ButtonStyle.red)
    async def hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=discord.Embed(title=f"Command {self.id} Killed"), ephemeral=True)
        self.running_commands_dict[self.id].kill()
        del self.running_commands_dict[self.id]

        self.stop()

    @discord.ui.button(emoji="🪶", style=discord.ButtonStyle.green)
    async def text_box(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal: discord.ui.Modal = EditWindow(self.running_commands_dict[self.id].info.message)
        # TODO find a way to prevent the assignment to happen immediately, and rather wait until the user has finished writing
        await interaction.response.send_modal(modal)
        
        while not modal.is_finished():
            await asyncio.sleep(1)
        self.running_commands_dict[self.id].info.message = modal.children[0].value


@tree.command(
    name="running_commands",
    description="See the currently running commands",
    guild=discord.Object(id=guild_id)
)
async def running_commands(ctx):
    if not running_commands_dict:
        await ctx.response.send_message(embed=discord.Embed(title="No commands running"), ephemeral=True)
        return

    await ctx.response.send_message(embed=discord.Embed(title="Showing all running processes"), ephemeral=True)

    for id, command in running_commands_dict.items():
        embed = command.get_embed()
        await ctx.channel.send(embed=embed, view = SimpleView(id, running_commands_dict))


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
    embed.add_field(name="/annoy <message> <amount> <interval>", 
                    value="Spams a given message at a given user", inline=False)
    embed.add_field(name="/dm_aga <message> <amount> <interval>", 
                    value="Sends a given personal message to HA", inline=False)
    embed.add_field(name="/get_attention <user> <message> <amount> <interval>", 
                    value="Sends the given message at the given user until they acnowledge that they have seen the message", inline=False)
    embed.add_field(name="/free_games_rn", 
                    value="See free games from Epic Games", inline=False)
    embed.add_field(name="/cleanup <messages_amount>", 
                    value="Deletes the given amount of messages", inline=False)
    embed.add_field(name="/running_commands", 
                    value="Manage running commands and see their IDs", inline=False)
    embed.add_field(name="/kill_command <ID>", 
                    value="Kills the command with the corresponding ID", inline=False)
    embed.add_field(name="/kill_all_commands", 
                    value="Kill all commands, try to use /kill_command first", inline=False)
    embed.set_footer(text="<interval> is in seconds, but can be evaluated by for example 20*60")

    await ctx.response.send_message(embed=embed, ephemeral=True)
