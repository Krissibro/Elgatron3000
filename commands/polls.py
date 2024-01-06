import discord

from utilities.shared import *
from collections import Counter
from utilities.helper_functions import char_to_emoji


class Dropdown(discord.ui.Select):
    votes = {}

    def __init__(self, message_ctx, title, description, option_text):
        self.message_ctx: discord.Interaction = message_ctx
        self.title = title
        self.description = description

        options = [discord.SelectOption(label=i) for i in option_text]
        super().__init__(placeholder="select what you wanna", min_values=1, max_values=3, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.votes[interaction.user.name] = self.values
        self.count_votes()

        await self.message_ctx.edit_original_response(content="test", embed=self.make_embed())

    def count_votes(self):
        c = Counter({i.value: 0 for i in self.options})  # init the counter with 0 for every value
        for i in self.votes.values():
            temp_c = Counter(i)
            c.update(temp_c)
        return c.items()

    def make_embed(self):
        embed = discord.Embed(title=self.title, description=self.description)
        for i, j in self.count_votes():
            embed.add_field(name=i, value=f"‎{':green_square:' * j}", inline=False)
        embed.set_footer(text=f"{', '.join(self.votes.keys())} has voted")
        return embed


class ManageCommandsDropDown(discord.ui.View):
    def __init__(self, message_ctx, title, description, options):
        super().__init__()
        self.add_item(Dropdown(message_ctx, title, description, options))


@tree.command(
    name="start_poll",
    description="start a poll",
    guild=discord.Object(id=guild_id)
)
async def start_poll(ctx: discord.Interaction, title: str, description: str, option1: str, option2: str,
                     option3: str = None, option4: str = None, option5: str = None,
                     option6: str = None, option7: str = None, option8: str = None, option9: str = None,
                     option10: str = None):
    options = [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10]
    options = [i for i in options if i]  # remove option if it's not defined
    view = ManageCommandsDropDown(ctx, title, description, options)
    first_embed = discord.Embed(title="test poll")
    await ctx.response.send_message(embed=first_embed, view=view)
    msg = await ctx.original_response()
    await msg.create_thread(name=title)


@tree.command(
    name="start_poll_simple",
    description="start a poll",
    guild=discord.Object(id=guild_id)
)
async def start_poll_simple(ctx: discord.Interaction, title: str, description: str, option1: str, option2: str,
                            option3: str = None, option4: str = None, option5: str = None,
                            option6: str = None, option7: str = None, option8: str = None, option9: str = None,
                            option10: str = None):
    options = [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10]
    options = [i for i in options if i]  # remove option if it's not defined
    embed = discord.Embed(title=title, description=description)
    for i, j in enumerate(options):
        embed.add_field(name=f"{char_to_emoji(i + 1)} {j}", value="", inline=False)
    await ctx.response.send_message(embed=embed)
    msg = await ctx.original_response()
    for i in range(len(options)):
        await msg.add_reaction(char_to_emoji(i + 1))
    await msg.create_thread(name=title)
