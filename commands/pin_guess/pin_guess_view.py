import discord
from typing import Optional

from commands.pin_guess.pin_guess_model import Pin


# TODO original message should not be .original response, and we should not ctx.response.send_message because that gives an object with limited availability
class PinView(discord.ui.View):
    def __init__(self, pin: Pin, timeout=60):
        super().__init__(timeout=timeout)
        self.pin: Pin = pin
        self.original_message: Optional[discord.InteractionMessage] = None


    def make_first_embed(self) -> discord.Embed:
        """Creates the embed containing the title and the selected pin.
        Also appends the attachments if there are any"""
        embed: discord.Embed = discord.Embed(title="Guess the pin!",
                                             description=self.pin.content if self.pin.content else None)
        return embed

    def make_sinner_embed(self) -> discord.Embed:
        if self.pin.message is None: # should technically never happen
            return discord.Embed(title="Result has not loaded yet!!",)

        embed: discord.Embed = self.make_first_embed()
        embed.add_field(name="By",
                        value=f"{self.pin.message.author}", inline=True)
        embed.add_field(name="Context",
                        value=self.pin.message.jump_url)
        return embed


    async def reveal_author(self):
        """Method to reveal the author and edit the original message."""
        if self.original_message is None:
            raise ValueError("Original message is undefined")
        sinner_embed = self.make_sinner_embed()
        await self.original_message.edit(embed=sinner_embed, view=None)

    async def on_timeout(self):
        await self.reveal_author()

    @discord.ui.button(label="Reveal the sinner!", style=discord.ButtonStyle.success)
    async def reveal_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.reveal_author()