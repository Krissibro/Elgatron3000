import discord.ui

from discord import app_commands
from discord.ext import commands

from utilities.settings import guild_id, active_commands


class MessageSelectDropdown(discord.ui.Select):
    def __init__(self):
        options = active_commands.make_dropdown_options()
        super().__init__(placeholder="Which command would you like to edit?", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        selected_command_id = int(self.values[0])

        if selected_command_id in active_commands.get_ids():
            embed = active_commands.get_command_embed(selected_command_id)
            view = ManageCommandsButtons(selected_command_id)
        else:
            embed = active_commands.make_overview_embed()
            view = ManageCommandsDropDown()
        await interaction.response.edit_message(embed=embed, view=view)

class ManageCommandsDropDown(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MessageSelectDropdown())


class ManageCommandsButtons(discord.ui.View):
    def __init__(self, command_id: int):
        super().__init__()
        self.command_id: int = command_id

    async def make_command_embed(self, interaction: discord.Interaction) -> None:
        if not active_commands.is_empty():
            view = ManageCommandsButtons(self.command_id)
            embed = active_commands[self.command_id].make_embed()
        else:
            view = None
            embed = discord.Embed(title="No commands running", color=discord.Color.red())
        await interaction.edit_original_response(embed=embed, view=view)

    async def return_to_dropdown(self, interaction: discord.Interaction) -> None:
        if not active_commands.is_empty():
            view = ManageCommandsDropDown()
            embed = active_commands.make_overview_embed()
        else:
            view = None
            embed = discord.Embed(title="No commands running", color=discord.Color.red())
        await interaction.edit_original_response(view=view, embed=embed)

    @discord.ui.button(emoji="📄", style=discord.ButtonStyle.blurple)
    async def return_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()

        await self.return_to_dropdown(interaction)

    @discord.ui.button(emoji="💀", style=discord.ButtonStyle.red)
    async def kill_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        await self.return_to_dropdown(interaction)

        if active_commands.check_if_command_exists(self.command_id):
            active_commands[self.command_id].kill()
            await active_commands[self.command_id].delete_messages()
            active_commands.kill(self.command_id)


    @discord.ui.button(emoji="🪶", style=discord.ButtonStyle.green)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:

        if active_commands.check_if_command_exists(self.command_id):
            modal = active_commands[self.command_id].get_edit_window()
            await interaction.response.send_modal(modal)
            await modal.finished_event.wait()  # Wait for the modal to be closed

            await self.make_command_embed(interaction)
        else:
            await self.return_to_dropdown(interaction)


class CommandManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="manage_commands",
        description="See and manage running commands"
    )
    async def manage_commands(self, ctx: discord.Interaction):
        if active_commands.is_empty():
            await ctx.response.send_message(embed=discord.Embed(title="No commands running", color=discord.Color.red()),
                                            ephemeral=True)
            return
        view = ManageCommandsDropDown()
        first_embed = active_commands.make_overview_embed()
        await ctx.response.send_message(embed=first_embed, view=view, ephemeral=True)

    @app_commands.command(
        name="cleanup",
        description="Clean the current chat for bot messages"
    )
    async def cleanup(self, ctx: discord.Interaction, messages_amount: int):
        if messages_amount <= 0:
            await ctx.response.send_message(embed=discord.Embed(title="Cannot delete less than 1 message"),
                                            ephemeral=True)
            return
        await ctx.response.defer()
        await ctx.channel.purge(limit=messages_amount, check=lambda m: m.author == self.bot.user)
        await ctx.response.send_message(embed=discord.Embed(title=f"Deleted {messages_amount} messages"),
                                        ephemeral=True,
                                        delete_after=10)


async def setup(bot):
    await bot.add_cog(CommandManagement(bot), guild=bot.get_guild(guild_id))