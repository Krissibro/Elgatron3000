import discord
from io import BytesIO
from PIL import Image, ImageSequence

from utilities.settings import guild_id, tree


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

        # get sizes
        canvas_width, canvas_height = template_gif.size
        avatar_width, avatar_height = int(canvas_width * 0.8), int(canvas_height * 0.8)

        frames = template_gif.n_frames
        max_stretch = 0.25

        stretch = [abs((i - frames//2)/(frames//2)) * max_stretch for i in range(frames)]
        pull = stretch[5:] + stretch[:5]

        print(stretch)
        print(pull)

        for i, hand_frame in enumerate(ImageSequence.Iterator(template_gif)):
            hand_frame = hand_frame.convert("RGBA")
            frame = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))

            # TODO stretch and squeeze the user avatar

            new_avatar_width = int(avatar_width * (1 - pull[i]))
            new_avatar_height = int(avatar_height * (1 - stretch[i]))

            avatar_x = canvas_width - new_avatar_width
            avatar_y = canvas_height - new_avatar_height

            # Paste avatar, then hand on top
            temp_avatar = avatar_image.resize((new_avatar_height, new_avatar_width))

            frame.paste(temp_avatar, (avatar_x, avatar_y), temp_avatar)
            frame.paste(hand_frame, (0, 0), hand_frame)

            images.append(frame)

    # save the gif
    img_byte_arr = BytesIO()
    images[0].save(
        img_byte_arr,
        format="GIF",
        save_all=True,
        append_images=images[1:],
        duration=30,
        disposal=2,  # 2 = Restore to background color.
        loop=0
    )
    img_byte_arr.seek(0)

    file = discord.File(fp=img_byte_arr, filename="petting.gif")
    await ctx.response.send_message(file=file)
