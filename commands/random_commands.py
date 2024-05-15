import discord

from utilities.settings import guild_id, tree


@tree.command(
    name="this_dude",
    description="this dude a dude",
    guild=discord.Object(id=guild_id)
)
async def this_dude(ctx: discord.Interaction):
    await ctx.response.send_message("https://tenor.com/view/this-dude-bro-bruh-welcome-to-gamestop-tiktok-gif-21824756")


@tree.command(
    name="pet_elga3",
    description="pet elga3 a bit",
    guild=discord.Object(id=guild_id)
)
async def pet_elga3(ctx: discord.Interaction):
    await ctx.response.send_message("https://media.discordapp.net/attachments/875799818621046855/917046780854685716/5f4877b8-0843-4369-b0dc-0238c230723b.gif?ex=65e47cde&is=65d207de&hm=d79d73354d613b62fdea18fbd782279f980ff19e0d7ad5c4cf51d66094cb655d&")


@tree.command(
    name="thanos_snapped",
    description="you just got thanos snapped",
    guild=discord.Object(id=guild_id)
)
async def thanos_snapped(ctx: discord.Interaction):
    await ctx.response.send_message("https://tenor.com/view/disappointed-snapped-sad-gif-22165289")


@tree.command(
    name="weave",
    description="weave",
    guild=discord.Object(id=guild_id)
)
async def weave(ctx: discord.Interaction):
    await ctx.response.send_message("https://cdn.discordapp.com/attachments/839100318893211669/1211047164567093248/weave.mov?ex=65ecc690&is=65da5190&hm=6ba609dcb85e8ccda9ed75850c0686117f0fa6f824bd6073d035c55a487c6131&")


@tree.command(
    name="trout",
    description="trout",
    guild=discord.Object(id=guild_id)
)
async def trout(ctx: discord.Interaction):
    await ctx.response.send_message("https://cdn.discordapp.com/attachments/839100318893211669/1211047338509082664/trout.mp4?ex=65ecc6b9&is=65da51b9&hm=53454f3fb04b5ac3c02974211f370897b90e3a1925f4d3e5c0ab5aee9dcd6077&")


