from command_objects.Command import *
from command_objects.MessagingInfo import *
from ast import literal_eval


async def validate_user(ctx:discord.Interaction, user:discord.User):
    if user is None:
        return True
    """ Doesnt work RN
    elif user in ctx.guild.members:
        await ctx.response.send_message(embed=discord.Embed(title="User could not be found"), ephemeral=True)
        return False
    """
    return True


async def validate_interval(ctx, interval):
    if interval <= 0:
        await ctx.response.send_message(embed=discord.Embed(title="Interval cannot be less than or equal to 0"), ephemeral=True)
        return False
    return True


async def validate_amount(ctx, amount):
    if amount <= 0:
        await ctx.response.send_message(embed=discord.Embed(title="Amount cannot be less than or equal to 0"), ephemeral=True)
        return False
    return True


async def execute_command(ctx, command_name, internal_function, user: discord.User, message: str, amount: int, interval:int, channel: discord.TextChannel):
    """
    Executes a specified command with validation, tracking, and response handling.

    Args:
        ctx (Context): The context in which the command is being executed.
        command_name (str): The name of the command to be executed.
        internal_function (Coroutine): The asynchronous function representing the command's logic.
        user (discord.User): The Discord user who is targeted or involved in the command.
        message (str): A message associated with the command.
        amount (int): The amount of times a command is to be executed.
        interval (int): The time intervals for the command's operation.
        channel (discord.TextChannel): The channel in which the command is being executed.

    Description:
        This function validates user input, creates a command with necessary information, and tracks it using a command tracker.
        It sends an ephemeral response message with the command details, executes the command, and cleans up after completion.
        If validation fails at any step, the function exits without executing the command.
    """

    # Error handling
    if not (await validate_user(ctx, user) and await validate_amount(ctx, amount) and await validate_interval(ctx, interval)):
        return

    # Create a Command object with the given information
    messaging_info = MessagingInfo(command_name, user, message, amount, interval, channel)
    async_task = asyncio.create_task(internal_function(ctx, messaging_info))
    command = Command(messaging_info, async_task)

    # Run the given command
    await ctx.response.send_message(embed=messaging_info.make_embed(), ephemeral=True, delete_after=10)
    await async_task

    # Clean up after Command
    command.end()


@tree.command(
    name="annoy",
    description="Spam a message at someone!",
    guild=discord.Object(id=guild_id)
)
async def annoy(ctx, message: str, amount: int, interval: str, user: discord.User = None):
    interval = literal_eval(interval)
    await execute_command(ctx, "annoy", annoy_internal, user, message, amount, interval, ctx.channel)


async def annoy_internal(ctx, command_info: MessagingInfo):
    while command_info.remaining > 0:
        command_info.remaining -= 1
        message = await ctx.channel.send(f"{command_info.user} {command_info.message}")
        command_info.add_message(message)
        await asyncio.sleep(command_info.interval)


@tree.command(
    name="dm_aga",
    description="Annoy HA as many times as you would like with a given interval!",
    guild=discord.Object(id=guild_id)
)
async def dm_aga(ctx, message: str, amount: int, interval: str):
    interval = literal_eval(interval)
    await execute_command(ctx, "dm_spam_internal", dm_spam_internal, client.fetch_user(276441391502983170), message, amount, interval, ctx.channel)


async def dm_spam_internal(ctx, command_info: MessagingInfo):
    try:
        while command_info.remaining > 0:
            command_info.remaining -= 1
            await command_info.user.send(command_info.message)
            await asyncio.sleep(command_info.interval)

    except discord.Forbidden:
        await ctx.followup.send(embed=discord.Embed(title="I don't have permission to send messages to that user!"), ephemeral=True)


@tree.command(
    name="get_attention",
    description="Ping someone once every 10 seconds 100 times or until they react",
    guild=discord.Object(id=guild_id)
)
async def get_attention(ctx, user: discord.User, message: str = "WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP", amount: int = 100, interval: str = "10"):
    interval = literal_eval(interval)
    await execute_command(ctx, "get_attention", get_attention_internal, user, message, amount, interval, ctx.channel)


class ReactButton(discord.ui.View):
    seen: bool = False

    @discord.ui.button(emoji="🤨", style=discord.ButtonStyle.success)
    async def wake_up_bitch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.send(f"New death grips album dropping tomorrow :pensive:")
        await interaction.response.defer()
        self.seen = True
        self.stop()


async def get_attention_internal(ctx, command_info: MessagingInfo):
    while command_info.remaining > 0:
        command_info.remaining -= 1
        view = ReactButton(timeout=command_info.interval * 2)

        message = await ctx.channel.send(command_info.user,
                                         embed=discord.Embed(title=f"{command_info.message}"),
                                         view=view)

        command_info.add_message(message)

        await asyncio.sleep(command_info.interval)
        if view.seen:
            await command_info.delete_messages()
            break
