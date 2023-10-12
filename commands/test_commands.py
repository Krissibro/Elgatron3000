from utilities.shared import *


class EditWindow(discord.ui.Modal):
    def __init__(self, old_message:str):
        super().__init__(title="Edit")
        self.add_item(discord.ui.TextInput(label="please enter the edit you want to make",
                                           style=discord.TextStyle.short,
                                           default=old_message))
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
    edit = EditWindow("test")
    # TODO find a way to prevent the assignment to happen immediately, and rather wait until the user has finished writing
    await ctx.response.send_modal(edit)

    while(not edit.submitted):
        await asyncio.sleep(1)
    
    print(edit.children[0])
