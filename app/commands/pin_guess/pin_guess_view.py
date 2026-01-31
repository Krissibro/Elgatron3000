import discord
import random

from app.models.pin_model import Pin

class PinView(discord.ui.View):
    def __init__(self, pin: Pin):
        super().__init__(timeout=None)
        self.pin: Pin = pin

    def make_first_embed(self) -> discord.Embed:
        """Creates the embed containing the title and the selected pin.
        Also appends the attachments if there are any"""
        embed: discord.Embed = discord.Embed(title="",
                                             description=self.pin.message_content,
                                             color=discord.Color.yellow())
        # result of deliberation
        title = random.choices(["Guess the pin!", "who dunnit?"], weights=[0.9, 0.1], k=1)[0]
        embed.set_author(name=title,
                         icon_url="https://media.discordapp.net/attachments/1217929494703374416/1458419529624588298/user.png")
        return embed

    def make_sinner_embed(self) -> discord.Embed:
        date = self.pin.created_at
        icon_url = self.pin.get_icon_link()
        url = self.pin.get_message_link()

        embed: discord.Embed = discord.Embed(title="",
                                             description=self.pin.message_content,
                                             color=discord.Color.green()
                                             )

        embed.set_author(name=f"{self.pin.user_name} on {date.strftime('%d/%m/%Y')}", icon_url=icon_url, url=url)
        return embed

    async def reveal_author(self, interaction: discord.Interaction) -> None:
        """Method to reveal the author and edit the original message."""
        sinner_embed = self.make_sinner_embed()
        await interaction.response.edit_message(embed=sinner_embed, view=None)

    @discord.ui.button(label="Reveal the sinner!", style=discord.ButtonStyle.success)
    async def reveal_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.reveal_author(interaction)

# does nothing, is just here to
class TempPinView(discord.ui.View):
    def __init__(self, timeout=60) -> None:
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Reveal the sinner!", style=discord.ButtonStyle.success, disabled=True)
    async def reveal_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass