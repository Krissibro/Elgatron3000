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
        self.submitted = False

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.submitted = True
        self.stop()

@tree.command(
    name="modal_test",
    description="testing forms",
    guild=discord.Object(id=guild_id)
)
async def modal_test(ctx: discord.Interaction):
    edit = EditWindow("test", 1, 2)
    await ctx.response.send_modal(edit)

    # TODO this works, but it sucks
    while(not edit.submitted):
        await asyncio.sleep(1)
    
    print(type(edit.children[0]))
    print(type(literal_eval(str(edit.children[1]))))

@tree.command(
    name="collect_data",
    description="testing data collection",
    guild=discord.Object(id=guild_id)
)
@app_commands.checks.bot_has_permissions(read_message_history = True)
async def collect_data(ctx: discord.Interaction):
    data = [[message.author.id, message.content] async for message in ctx.channel.history(limit = 10, )]
    print(data)
