import discord.ui
import asyncio

from ast import literal_eval

from discord import app_commands
from discord.ext import commands

from command_objects.Command import Command
from commands.messaging_commands import MessagingInfo
from utilities.helper_functions import parse_time, format_seconds, validate_numeric, validate_interval, validate_amount
from utilities.settings import guild_id


class MessageSelectDropdown(discord.ui.Select):
    def __init__(self):
        options = Command.make_dropdown_options()
        super().__init__(placeholder="Which command would you like to edit?", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        selected_command_id = int(self.values[0])

        if selected_command_id in Command.get_ids():
            await interaction.response.edit_message(
                embed=Command.get_embed_by_id(selected_command_id),
                view=ManageCommandsButtons(Command.get_command(selected_command_id)))

        else:
            await interaction.response.edit_message(
                embed=Command.make_overview_embed(),
                view=ManageCommandsDropDown()
            )


class ManageCommandsDropDown(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MessageSelectDropdown())


class ManageCommandsButtons(discord.ui.View):
    def __init__(self, command):
        super().__init__()
        self.command = command

    async def make_command_embed(self, interaction: discord.Interaction) -> None:
        if not Command.is_empty():
            view = ManageCommandsButtons(self.command)
            embed = self.command.get_embed()
        else:
            view = None
            embed = discord.Embed(title="No commands running", color=discord.Color.red())
        await interaction.edit_original_response(embed=embed, view=view)

    async def return_to_dropdown(self, interaction: discord.Interaction) -> None:
        if not Command.is_empty():
            view = ManageCommandsDropDown()
            embed = Command.make_overview_embed()
        else:
            view = None
            embed = discord.Embed(title="No commands running", color=discord.Color.red())
        await interaction.response.edit_message(view=view, embed=embed)

    @staticmethod
    @discord.ui.button(emoji="📄", style=discord.ButtonStyle.blurple)
    async def return_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.return_to_dropdown(interaction)

    @discord.ui.button(emoji="💀", style=discord.ButtonStyle.red)
    async def kill_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await self.silliness_check(interaction):
            self.command.kill()
            await self.return_to_dropdown(interaction)
            await self.command.info.delete_messages()

    @discord.ui.button(emoji="🪶", style=discord.ButtonStyle.green)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await self.silliness_check(interaction):
            modal = EditMessagingCommandWindow(self.command.info)
            await interaction.response.send_modal(modal)
            await modal.finished_event.wait()  # Wait for the modal to be closed

            await self.make_command_embed(interaction)

    # Check if the command still exists
    async def silliness_check(self, interaction: discord.Interaction) -> bool:
        """
        :param interaction: interaction tied to command management message.
        :return: True if command exists in the command list. else False
        """
        if not Command.check_if_command_exists(self.command.id):
            await self.return_to_dropdown(interaction)
            return False
        return True


class EditMessagingCommandWindow(discord.ui.Modal):
    def __init__(self, command_info: MessagingInfo) -> None:
        super().__init__(title="Edit")
        self.command_info = command_info

        self.message_input = discord.ui.TextInput(
            label="Message:",
            style=discord.TextStyle.short,
            default=command_info.message
        )
        self.amount_input = discord.ui.TextInput(
            label="Amount:",
            style=discord.TextStyle.short,
            default=str(command_info.remaining)
        )
        self.interval_input = discord.ui.TextInput(
            label="Interval:",
            style=discord.TextStyle.short,
            default=format_seconds(command_info.interval)
        )
        self.add_item(self.message_input)
        self.add_item(self.amount_input)
        self.add_item(self.interval_input)

        self.finished_event = asyncio.Event()

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if (
            not await validate_numeric(interaction, self.amount_input.value, "Amount must be numeric") or
            not await validate_amount(interaction, int(self.amount_input.value)) or
            not await validate_interval(interaction, parse_time(self.interval_input.value))
        ):
            self.stop()
            self.finished_event.set()
            return
        await interaction.response.defer()

        self.command_info.message = self.message_input.value
        self.command_info.amount = literal_eval(self.amount_input.value)
        self.command_info.remaining = literal_eval(self.amount_input.value)
        self.command_info.interval = parse_time(self.interval_input.value)

        self.stop()
        self.finished_event.set()  # Signal that the modal is closed


class CommandManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="manage_commands",
        description="See and manage running commands"
    )
    async def manage_commands(self, ctx: discord.Interaction):
        if Command.is_empty():
            await ctx.response.send_message(embed=discord.Embed(title="No commands running", color=discord.Color.red()),
                                            ephemeral=True)
            return
        view = ManageCommandsDropDown()
        first_embed = Command.make_overview_embed()
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