from typing import List

import discord

from app.commands.messaging.ActiveCommands import ActiveCommands

class MessageSelectDropdown(discord.ui.Select):
    def __init__(self, active_commands: ActiveCommands):
        self.active_commands: ActiveCommands = active_commands
        options: List[discord.SelectOption] = active_commands.make_dropdown_options()
        super().__init__(placeholder="Which command would you like to edit?", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        selected_command_id = int(self.values[0])

        if selected_command_id in self.active_commands.get_ids():
            embed = self.active_commands.get_command_embed(selected_command_id)
            view = ManageCommandsButtons(selected_command_id, self.active_commands)
        else:
            embed = self.active_commands.make_overview_embed()
            view = ManageCommandsDropDown(self.active_commands)
        await interaction.response.edit_message(embed=embed, view=view)

class ManageCommandsDropDown(discord.ui.View):
    def __init__(self, active_commands: ActiveCommands):
        super().__init__()
        self.add_item(MessageSelectDropdown(active_commands))


class ManageCommandsButtons(discord.ui.View):
    def __init__(self, command_id: int, active_commands: ActiveCommands):
        super().__init__()
        self.active_commands: ActiveCommands = active_commands
        self.command_id: int = command_id

    async def make_command_embed(self, interaction: discord.Interaction) -> None:
        if not self.active_commands.is_empty():
            view = ManageCommandsButtons(self.command_id, self.active_commands)
            embed = self.active_commands[self.command_id].make_embed()
        else:
            view = None
            embed = discord.Embed(title="No commands running", color=discord.Color.red())
        await interaction.edit_original_response(embed=embed, view=view)

    async def return_to_dropdown(self, interaction: discord.Interaction) -> None:
        if not self.active_commands.is_empty():
            view = ManageCommandsDropDown(self.active_commands)
            embed = self.active_commands.make_overview_embed()
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

        if self.active_commands.check_if_command_exists(self.command_id):
            await self.active_commands.kill(self.command_id)

        await self.return_to_dropdown(interaction)


    @discord.ui.button(emoji="🪶", style=discord.ButtonStyle.green)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:

        if self.active_commands.check_if_command_exists(self.command_id):
            modal = self.active_commands[self.command_id].get_edit_window(interaction)
            await interaction.response.send_modal(modal)
            await modal.wait()  # Wait for the modal to be closed

        await self.make_command_embed(interaction)
