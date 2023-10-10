from utilities.shared import *


class Edit_window(discord.ui.Modal, title = "Edit"):
    field = discord.ui.TextInput(label="please enter the edit you want to make", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


@tree.command(
    name="modal_test",
    description="testing forms",
    guild=discord.Object(id=guild_id)
)
async def modal_test(ctx: discord.Interaction):
    await ctx.response.send_modal(Edit_window())
