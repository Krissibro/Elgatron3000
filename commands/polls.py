import discord

from utilities.shared import *
from collections import Counter


class Dropdown(discord.ui.Select):
    votes = {}

    def __init__(self, message_ctx):
        super().__init__()
        self.message_ctx: discord.Interaction = message_ctx
        options = [discord.SelectOption(label=str(i)) for i in [1, 2, 3]]
        super().__init__(placeholder="select what you wanna", min_values=1, max_values=3, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.votes[interaction.user] = self.values
        self.count_votes()

        await self.message_ctx.edit_original_response(content="test", embed=self.make_embed())

    def count_votes(self):
        c = Counter({i.value: 0 for i in self.options})  # init the counter with 0 for every value
        for i in self.votes.values():
            temp_c = Counter(i)
            c.update(temp_c)
        return c.items()

    def make_embed(self):
        embed = discord.Embed(title="Poll", description="vote info")
        for i, j in self.count_votes():
            embed.add_field(name=i, value=":green_square:"*j, inline=False)
        return embed


class ManageCommandsDropDown(discord.ui.View):
    def __init__(self, message_ctx):
        super().__init__()
        self.add_item(Dropdown(message_ctx))


@tree.command(
    name="start_poll",
    description="start a poll",
    guild=discord.Object(id=guild_id)
)
async def start_poll(ctx):
    view = ManageCommandsDropDown(ctx)
    first_embed = discord.Embed(title="test poll")
    await ctx.response.send_message(embed=first_embed, view=view, ephemeral=True)
