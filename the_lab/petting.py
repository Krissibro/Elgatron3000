import discord
from io import BytesIO
from PIL import Image, ImageSequence

from utilities.shared import tree
from utilities.settings import guild_id


@tree.command(
    name="petting",
    description="give people pets!",
    guild=discord.Object(id=guild_id)
)
async def petting(ctx, user: discord.User):
    # Get the profile picture
    avatar = BytesIO()
    await user.display_avatar.save(fp=avatar, seek_begin=True)
    avatar_image = Image.open(avatar).convert("RGBA")

    # go through the frames of the gif
    images = []
    with open("data/template.gif", "rb") as f:
        template_gif = Image.open(f)
        for frame in ImageSequence.Iterator(template_gif):
            frame = frame.convert("RGBA")  # Ensure frame is in RGBA mode

            # Create a copy of the avatar image for each frame
            frame_avatar = avatar_image.copy()

            # TODO makes sure the avatar and frames are alligned correctly

            # TODO squish and pull the avatar

            # Paste the frame on top of the avatar image
            frame_avatar.paste(frame, (0, 0), frame)
            images.append(frame_avatar)

    # save the gif
    img_byte_arr = BytesIO()
    images[0].save(
        img_byte_arr,
        format="GIF",
        save_all=True,
        append_images=images[1:],
        duration=30,
        loop=0
    )
    img_byte_arr.seek(0)

    # Send the GIF
    file = discord.File(fp=img_byte_arr, filename="petting.gif")
    await ctx.response.send_message(file=file)