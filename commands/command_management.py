from command_objects.Command import *
from commands.messaging_commands import *
from ast import literal_eval


def ids():
    return Command.get_ids()


async def get_first_embed():
    return Command.get_embed_by_id(ids()[0])


class ManageCommandsButtons(discord.ui.View):
    def __init__(self, message_ctx):
        super().__init__()
        self.current_page = 1
        self.message_ctx = message_ctx

    async def update_embed(self, interaction: discord.Interaction):
        view = self if len(ids()) > 0 else None
        embed = Command.get_embed_by_id(ids()[self.current_page]) if len(ids()) > 0 \
            else discord.Embed(title="There are no more running commands")

        await self.message_ctx.edit_original_response(embed=embed, view=view)

    @discord.ui.button(emoji="◀", style=discord.ButtonStyle.blurple)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page - 1) % len(ids())
        await self.update_embed(interaction)
        await interaction.response.defer()

    @discord.ui.button(emoji="💀", style=discord.ButtonStyle.red)
    async def kill_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        current_command = Command.get_command(ids()[self.current_page])
        current_command.kill()
        # del ids()[self.current_page]
        self.current_page = min(self.current_page, len(ids()) - 1)

        await self.update_embed(interaction)

        await current_command.info.delete_messages()

    @discord.ui.button(emoji="🪶", style=discord.ButtonStyle.green)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        current_command = Command.get_command(ids()[self.current_page])
        command_info = current_command.info

        modal = EditMessagingCommandWindow(command_info)
        await interaction.response.send_modal(modal)

        await modal.finished_event.wait()  # Wait for the modal to be closed

        await self.update_embed(interaction)

    @discord.ui.button(emoji="▶", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page + 1) % len(ids())
        await self.update_embed(interaction)
        await interaction.response.defer()


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
            default=str(command_info.interval)
        )
        self.add_item(self.message_input)
        self.add_item(self.amount_input)
        self.add_item(self.interval_input)

        self.finished_event = asyncio.Event()

    async def on_submit(self, interaction: discord.Interaction):
        if (not await validate_amount(interaction, literal_eval(self.amount_input.value))
                or not await validate_interval(interaction, literal_eval(self.interval_input.value))):
            self.finished_event.set()
            return

        await interaction.response.defer()

        self.command_info.message = self.message_input.value
        self.command_info.amount = literal_eval(self.amount_input.value)
        self.command_info.remaining = literal_eval(self.amount_input.value)
        self.command_info.remaining = literal_eval(self.amount_input.value)

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

    view = ManageCommandsButtons(ctx)
    first_embed = await get_first_embed()
    await ctx.response.send_message(embed=first_embed, view=view, ephemeral=True)


@tree.command(
    name="kill_all_commands",
    description="Kill all running commands",
    guild=discord.Object(id=guild_id)
)
async def kill_all_commands(ctx):
    Command.kill_all()

    await ctx.response.send_message(embed=discord.Embed(title="All running commands have been terminated."),
                                    ephemeral=True)


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
