from utilities.shared import *
from ast import literal_eval


async def validate_user(ctx:discord.Interaction, user:discord.User):
    if user is None:
        return True
    elif ctx.guild.get_member(user.id) is None:
        await ctx.response.send_message(embed=discord.Embed(title="User could not be found"), ephemeral=True)
        return False
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


async def execute_command(ctx, command_name, internal_function, user: discord.User, message: str, amount: int, interval:int):
    # Error handling
    if not (await validate_user(ctx, user) and await validate_amount(ctx, amount) and await validate_interval(ctx, interval)):
        return

    # Make Command info
    command_info = MessagingInfo(command_name, user, message, amount, interval)
    
    # Make Command and add to command Tracker
    command = asyncio.create_task(internal_function(ctx, command_info))
    command_tracker = Command(command_info, command)
    running_commands_dict[command_tracker.id] = command_tracker

    # Run Command
    await ctx.response.send_message(embed=command_info.make_embed(), ephemeral=True)
    await command

    # Clean up after Command
    del running_commands_dict[command_tracker.id]
    Command.current_ids.remove(command_tracker.id)


@tree.command(
    name="annoy",
    description="Spam a message at someone!",
    guild=discord.Object(id=guild_id)
)
async def annoy(ctx, message: str, amount: int, interval: str, user: discord.User = None):
    interval = literal_eval(interval)
    await execute_command(ctx, "annoy", annoy_internal, user, message, amount, interval)


async def annoy_internal(ctx, command_info: MessagingInfo):
    while command_info.remaining > 0:
        command_info.remaining -= 1
        message = await ctx.channel.send(f"{command_info.user} {command_info.message}")
        command_info.messages.append(message)
        await asyncio.sleep(command_info.interval)


@tree.command(
    name="dm_aga",
    description="Annoy HA as many times as you would like with a given interval!",
    guild=discord.Object(id=guild_id)
)
async def dm_aga(ctx, message: str, amount: int, interval: str):
    interval = literal_eval(interval)
    await execute_command(ctx, "dm_spam_internal", dm_spam_internal, client.fetch_user(276441391502983170), message, amount, interval)


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
    description="Ping someone X times, once every 60 seconds until they react",
    guild=discord.Object(id=guild_id)
)
async def get_attention(ctx, message: str, amount: int, interval: str, user: discord.User):
    interval = literal_eval(interval)
    await execute_command(ctx, "get_attention", get_attention_internal, user, message, amount, interval)


class SeenButton(discord.ui.View):
    seen: bool = False

    @discord.ui.button(emoji="👍", style=discord.ButtonStyle.success)
    async def hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=discord.Embed(
            title=f"Okay, i will stop annoying you now {interaction.user.nick} :)"))
        self.seen = True
        self.stop()


async def get_attention_internal(ctx, command_info: MessagingInfo):
    while command_info.remaining > 0:
        command_info.remaining -= 1
        view = SeenButton(timeout=command_info.interval * 2)

        message = await ctx.channel.send(
            f"{command_info.user}",
            embed=discord.Embed(
                title=f"{command_info.message}",
                description="Press the button to stop being notified"
                ),
            view = view
            )
        
        command_info.messages.append(message)
        
        await asyncio.sleep(command_info.interval)
        if view.seen:
            break
