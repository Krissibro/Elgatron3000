import discord
from typing import Optional
from commands.pin_guess.pin_guess_model import Pin

# TODO original message should not be .original response, and we should not ctx.response.send_message because that gives an object with limited availability
class PinView(discord.ui.View):
    def __init__(self, message_ctx, pin, timeout=14*60):
        super().__init__(timeout=timeout)
        self.pin: Pin = pin
        self.message_ctx: discord.Interaction = message_ctx
        self.original_message: Optional[discord.InteractionMessage] = None

    def make_first_embed(self) -> discord.Embed:
        """Creates the embed containing the title and the selected pin.
        Also appends the attachments if there are any"""
        embed: discord.Embed = discord.Embed(title="Guess the pin!",
                                             description=self.pin.content if self.pin.content else None)
        return embed

    def make_sinner_embed(self) -> discord.Embed:
        embed: discord.Embed = self.make_first_embed()
        embed.add_field(name="By",
                        value=f"{self.pin.author}", inline=True)
        # TODO add guild_ID to pin, this solution works alright for now, but having it as a part of the pin object is prolly better
        embed.add_field(name="Context",
                        value=f"https://discord.com/channels/{self.message_ctx.guild_id}/{self.pin.channel_id}/{self.pin.message_id}")
        return embed

    async def send_attachments(self) -> None:
        """Sends the attachments of the pin to the channel if there are any.
        Must be called AFTER the initial response"""
        self.original_message = await self.message_ctx.original_response()
        if self.pin.attachments:
            await self.original_message.reply("\n".join(attachment for attachment in self.pin.attachments))

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