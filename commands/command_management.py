import discord.ui

from command_objects.Command import *
from commands.messaging_commands import *
from ast import literal_eval
from utilities.helper_functions import parse_time, format_seconds


class MessageSelectDropdown(discord.ui.Select):
    def __init__(self, message_ctx):
        self.message_ctx = message_ctx
        options = Command.make_dropdown_options()
        super().__init__(placeholder="Which command would you like to edit?", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_command_id = int(self.values[0])

        if selected_command_id in Command.get_ids():
            await interaction.response.defer()
            await self.message_ctx.edit_original_response(
                embed=Command.get_embed_by_id(selected_command_id),
                view=ManageCommandsButtons(self.message_ctx,
                                           command=Command.get_command(selected_command_id)))

        else:
            await interaction.response.send_message(embed=discord.Embed(title="This command is no longer running"),
                                                    ephemeral=True, delete_after=10)
            await self.message_ctx.edit_original_response(embed=Command.make_overview_embed(),
                                                          view=ManageCommandsDropDown(self.message_ctx))


class ManageCommandsDropDown(discord.ui.View):
    def __init__(self, message_ctx):
        super().__init__()
        self.add_item(MessageSelectDropdown(message_ctx))


class ManageCommandsButtons(discord.ui.View):
    def __init__(self, message_ctx, command):
        super().__init__()
        self.message_ctx = message_ctx
        self.command = command

    async def make_command_embed(self):
        view = ManageCommandsButtons(self.message_ctx, self.command) if not Command.is_empty() else None
        embed = self.command.get_embed() if not Command.is_empty() \
            else discord.Embed(title="There are no more running commands")

        await self.message_ctx.edit_original_response(embed=embed, view=view)

    async def return_to_dropdown(self):
        view = ManageCommandsDropDown(self.message_ctx) if not Command.is_empty() else None
        embed = Command.make_overview_embed() if not Command.is_empty() else discord.Embed(
            title="There are no more running commands",
            color=discord.Color.red())
        await self.message_ctx.edit_original_response(view=view, embed=embed)

    @discord.ui.button(emoji="📄", style=discord.ButtonStyle.blurple)
    async def return_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.return_to_dropdown()

    @discord.ui.button(emoji="💀", style=discord.ButtonStyle.red)
    async def kill_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.silliness_check(interaction):
            await interaction.response.defer()
            self.command.kill()
            await self.return_to_dropdown()
            await self.command.info.delete_messages()

    @discord.ui.button(emoji="🪶", style=discord.ButtonStyle.green)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.silliness_check(interaction):
            modal = EditMessagingCommandWindow(self.command.info)
            await interaction.response.send_modal(modal)
            await modal.finished_event.wait()  # Wait for the modal to be closed

            await self.make_command_embed()

    # Check if the command still exists
    async def silliness_check(self, interaction: discord.Interaction):
        if not Command.check_if_command_exists(self.command.id):
            await interaction.response.send_message(embed=discord.Embed(title="This command is no longer running"),
                                                    ephemeral=True, delete_after=10)
            await self.return_to_dropdown()
            return False
        return True


class EditMessagingCommandWindow(discord.ui.Modal):
    def __init__(self, command_info: MessagingInfo):
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
            default=str(command_info.amount)
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

    async def on_submit(self, interaction: discord.Interaction):
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


@tree.command(
    name="manage_commands",
    description="See and manage running commands",
    guild=discord.Object(id=guild_id)
)
async def manage_commands(ctx):
    if Command.is_empty():
        await ctx.response.send_message(embed=discord.Embed(title="No commands running"), ephemeral=True)
        return
    view = ManageCommandsDropDown(ctx)
    first_embed = Command.make_overview_embed()
    await ctx.response.send_message(embed=first_embed, view=view, ephemeral=True)


@tree.command(
    name="kill_all_commands",
    description="Kill all running commands",
    guild=discord.Object(id=guild_id)
)
async def kill_all_commands(ctx):
    await ctx.response.send_message(embed=discord.Embed(title="All running commands have been terminated."),
                                    ephemeral=True,
                                    delete_after=10)

    Command.kill_all()


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
    await ctx.response.send_message(embed=discord.Embed(title=f"Deleted {messages_amount} messages"),
                                    ephemeral=True,
                                    delete_after=10)


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
    embed.add_field(name="/get_attention <user> <message> <amount> <interval> ",
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
