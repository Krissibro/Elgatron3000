import discord

from commands.messaging.messaging.MessagingInfo import MessagingInfo


class ReactButton(discord.ui.View):
    @discord.ui.button(emoji="🤨", style=discord.ButtonStyle.success)
    async def wake_up_bitch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("New death grips album dropping tomorrow :pensive:")
        self.stop()


async def get_attention_internal(messaging_info: MessagingInfo) -> None:
    mention = messaging_info.get_mention()
    button = ReactButton(timeout=messaging_info.interval.seconds * 2)
    embed = discord.Embed(title=f"{messaging_info.message}")

    message = await messaging_info.channel.send(mention, embed=embed, view=button)
    messaging_info.add_message(message) # message added to list so that it can be deleted in the future.


async def dm_spam_internal(messaging_info: MessagingInfo) -> None:
    try:
        # these two should technically never happen 
        if isinstance(messaging_info.target, discord.Role):
            raise ValueError("Target user is invalid.")
        if messaging_info.target is None:
            raise ValueError("Target user is invalid.")
    
        message = await messaging_info.target.send(messaging_info.message)
        messaging_info.add_message(message)

    except (discord.Forbidden, discord.HTTPException, ValueError):
        embed = discord.Embed(title="I don't have permission to message that user.")
        await messaging_info.channel.send(embed=embed)
        

async def annoy_internal(messaging_info: MessagingInfo) -> None:
    message = await messaging_info.channel.send(f"{messaging_info.get_mention()} {messaging_info.message}")
    messaging_info.add_message(message)