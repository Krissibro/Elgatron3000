import discord

from utilities.settings import active_commands

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
            await modal.wait()  # Wait for the modal to be closed

        await self.make_command_embed(interaction)