import discord
from io import BytesIO
from PIL import Image, ImageSequence
from discord import app_commands
from discord.ext import commands

from utilities.elgatron import Elgatron


class Petting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="petting",
        description="give people pets!"
    )
    async def petting(self, ctx, user: discord.User):
        # Get the profile picture
        avatar = BytesIO()
        await user.display_avatar.save(fp=avatar, seek_begin=True)
        avatar_image = Image.open(avatar).convert("RGBA")

        # go through the frames of the gif

        file = await petting(avatar_image)

        await ctx.response.send_message(file=file)


async def petting(avatar_image: Image.Image) -> discord.File:
    frames_out = []
    squash_and_stretch = [
        (1.00, 1.00),  # frame 0
        (0.97, 1.03),  # frame 0
        (0.94, 1.06),  # frame 1
        (0.91, 1.09),  # frame 1
        (0.88, 1.12),  # frame 2
        (0.88, 1.12),  # frame 2
        (0.91, 1.09),  # frame 3
        (0.94, 1.06),  # frame 3
        (0.97, 1.03),  # frame 4
        (1.00, 1.00)  # frame 4
    ]

    # Load template hand gif
    with open("data/template.gif", "rb") as f:
        template = Image.open(f)

        canvas_w, canvas_h = template.size
        base_size = int(canvas_w * 0.75)

        # Force avatar square (pet-pet standard)
        avatar_image = avatar_image.resize((base_size, base_size), Image.LANCZOS)

        for i, hand_frame in enumerate(ImageSequence.Iterator(template)):
            # Loop scale values across frames
            scale = squash_and_stretch[i % len(squash_and_stretch)]
            sx, sy = scale

            # Resize avatar with squeeze/stretch
            resized_avatar = avatar_image.resize(
                (int(base_size * sx), int(base_size * sy)),
                Image.LANCZOS
            )

            # Center the avatar on canvas
            vertical_offset = 10
            horizontal_offset = 6
            ax = (canvas_w - resized_avatar.width) // 2 + horizontal_offset
            ay = (canvas_h - resized_avatar.height) // 2 + vertical_offset

            # Prepare final frame
            frame = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
            frame.paste(resized_avatar, (ax, ay), resized_avatar)

            hand = hand_frame.convert("RGBA")
            frame.paste(hand, (0, 0), hand)

            frames_out.append(frame)

    # Export GIF
    out = BytesIO()
    frames_out[0].save(
        out,
        format="GIF",
        save_all=True,
        append_images=frames_out[1:],
        duration=30,
        loop=0,
        disposal=2
    )
    out.seek(0)
    return discord.File(out, filename="petting.gif")



async def setup(bot: Elgatron):
    await bot.add_cog(Petting(bot), guild=discord.Object(id=bot.guild_id))
