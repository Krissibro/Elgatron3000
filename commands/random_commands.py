import discord
from discord.ext import commands
from discord import app_commands

from utilities.settings import guild_id


class StimCommands(commands.GroupCog, group_name="stim"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="this_dude",
        description="this dude a dude",
    )
    async def this_dude(self, ctx: discord.Interaction):
        await ctx.response.send_message("https://tenor.com/view/this-dude-bro-bruh-welcome-to-gamestop-tiktok-gif-21824756")

    @app_commands.command(
        name="pet_elga3",
        description="pet elga3 a bit",
    )
    async def pet_elga3(self, ctx: discord.Interaction):
        await ctx.response.send_message("https://media.discordapp.net/attachments/875799818621046855/917046780854685716/5f4877b8-0843-4369-b0dc-0238c230723b.gif?ex=65e47cde&is=65d207de&hm=d79d73354d613b62fdea18fbd782279f980ff19e0d7ad5c4cf51d66094cb655d&")

    @app_commands.command(
        name="thanos_snapped",
        description="you just got thanos snapped",
    )
    async def thanos_snapped(self, ctx: discord.Interaction):
        await ctx.response.send_message("https://tenor.com/view/disappointed-snapped-sad-gif-22165289")

    @app_commands.command(
        name="weave",
        description="weave",
    )
    async def weave(self, ctx: discord.Interaction):
        await ctx.response.send_message("https://cdn.discordapp.com/attachments/839100318893211669/1211047164567093248/weave.mov?ex=65ecc690&is=65da5190&hm=6ba609dcb85e8ccda9ed75850c0686117f0fa6f824bd6073d035c55a487c6131&")

    @app_commands.command(
        name="trout",
        description="trout",
    )
    async def trout(self, ctx: discord.Interaction):
        await ctx.response.send_message("https://cdn.discordapp.com/attachments/839100318893211669/1211047338509082664/trout.mp4?ex=65ecc6b9&is=65da51b9&hm=53454f3fb04b5ac3c02974211f370897b90e3a1925f4d3e5c0ab5aee9dcd6077&")

    @app_commands.command(
        name="sus",
        description="amogos sos amogos sossi sossi baki amogos sos amogos",
    )
    async def sussy_baki(self, ctx: discord.Interaction):
        await ctx.response.send_message("https://cdn.discordapp.com/attachments/839100318893211669/1245765875462836388/Sossi-baki.mp4?ex=6659f161&is=66589fe1&hm=5af0e663626613c8ef2ab2bb7c0876447eeeedc6194d7aa24f7c80c8dbb95d40&")

    @app_commands.command(
        name="minecraft",
        description="I be placing blocks n shit, cuz im in fucking minecraft",
    )
    async def minecraft(self, ctx: discord.Interaction):
        await ctx.response.send_message("https://cdn.discordapp.com/attachments/839100318893211669/1281936983135879262/minecraft.mp4?ex=66dd885a&is=66dc36da&hm=01e0ecc04e358363d36ee5c79fc6fe717b2b815844c31a6a6438d57a2b9b188e&")

    @app_commands.command(
        name="help",
        description="Gee you already know im obsessed with it *burp*, i cant get enough, back with another milk- ",
    )
    async def help(self, ctx: discord.Interaction):
        await ctx.response.send_message("https://cdn.discordapp.com/attachments/839100318893211669/1310589750490562640/HEEEELP.mp4?ex=6745c552&is=674473d2&hm=86c7673380acaf4bea501ca6cd938ba70da9ed7aa783882fa4445ef98c02ba85&")

    @app_commands.command(
        name="wassup_beijing",
        description="Christian winnie the pooh cosplay",
    )
    async def wassup_beijing(self, ctx: discord.Interaction):
        await ctx.response.send_message("https://cdn.discordapp.com/attachments/839100318893211669/1310925320014008340/wassup-beijing.mp4?ex=6746fdd8&is=6745ac58&hm=f3e680140b5238a1f6ec58b7c8ba95c7223e1fcc5246028dc7ba797be7d6f128&")

    @app_commands.command(
        name="gn_girl",
        description="*Rambunctious falling sounds*",
    )
    async def gn_girl(self, ctx: discord.Interaction):
        await ctx.response.send_message("https://cdn.discordapp.com/attachments/839100318893211669/1310925339765248020/gn-girl.mp4?ex=6746fddc&is=6745ac5c&hm=b4168328e4f76d27e2649dc530bf33b69fcdc60c72a29f54d847bab35ac8b907&")

    @app_commands.command(
        name="dr_peppa",
        description="Epic dr pebba prank",
    )
    async def dr_peppa(self, ctx: discord.Interaction):
        await ctx.response.send_message("https://cdn.discordapp.com/attachments/839100318893211669/1351897109263290479/dr-peppa.mp4?ex=67dc0bcb&is=67daba4b&hm=3c104e683e6274cd6dccb001ba942fc71dc446c127e3c107fff159b5b456b418&")


async def setup(bot):
    await bot.add_cog(StimCommands(bot), guild=bot.get_guild(guild_id))
