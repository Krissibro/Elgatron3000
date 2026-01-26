import random

import discord
from discord.ext import commands
from discord import app_commands

from app.core.elgatron import Elgatron

# Helper function to send media
# Takes either a single URL (str) or a list of URLs (list[str]) and sends one of them
async def send_media(ctx: discord.Interaction, media_urls: list[str] | str):
    if isinstance(media_urls, str):
        selected_media = media_urls
    else:
        selected_media = random.choice(media_urls)

    await ctx.response.send_message(selected_media)


class StimCommands(commands.GroupCog, group_name="stim"):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot

    @app_commands.command(
        name="this_dude",
        description="this dude a dude",
    )
    async def this_dude(self, ctx: discord.Interaction):
        await send_media(ctx, "https://tenor.com/view/this-dude-bro-bruh-welcome-to-gamestop-tiktok-gif-21824756")

    @app_commands.command(
        name="pet_elga3",
        description="pet elga3 a bit",
    )
    async def pet_elga3(self, ctx: discord.Interaction):
        await send_media(ctx, "https://media.discordapp.net/attachments/875799818621046855/917046780854685716/5f4877b8-0843-4369-b0dc-0238c230723b.gif?ex=65e47cde&is=65d207de&hm=d79d73354d613b62fdea18fbd782279f980ff19e0d7ad5c4cf51d66094cb655d&")

    @app_commands.command(
        name="thanos_snapped",
        description="you just got thanos snapped",
    )
    async def thanos_snapped(self, ctx: discord.Interaction):
        await send_media(ctx, "https://tenor.com/view/disappointed-snapped-sad-gif-22165289")

    @app_commands.command(
        name="weave",
        description="weave",
    )
    async def weave(self, ctx: discord.Interaction):
        await send_media(ctx, "https://cdn.discordapp.com/attachments/839100318893211669/1211047164567093248/weave.mov?ex=65ecc690&is=65da5190&hm=6ba609dcb85e8ccda9ed75850c0686117f0fa6f824bd6073d035c55a487c6131&")

    @app_commands.command(
        name="trout",
        description="trout",
    )
    async def trout(self, ctx: discord.Interaction):
        await send_media(ctx, "https://cdn.discordapp.com/attachments/839100318893211669/1211047338509082664/trout.mp4?ex=65ecc6b9&is=65da51b9&hm=53454f3fb04b5ac3c02974211f370897b90e3a1925f4d3e5c0ab5aee9dcd6077&")

    @app_commands.command(
        name="sus",
        description="amogos sos amogos sossi sossi baki amogos sos amogos",
    )
    async def sussy_baki(self, ctx: discord.Interaction):
        await send_media(ctx, "https://cdn.discordapp.com/attachments/839100318893211669/1245765875462836388/Sossi-baki.mp4?ex=6659f161&is=66589fe1&hm=5af0e663626613c8ef2ab2bb7c0876447eeeedc6194d7aa24f7c80c8dbb95d40&")

    @app_commands.command(
        name="crazy_jorgen_wordle_guess",
        description="We are onto you Jorgen",
    )
    async def crazy_jorgen_wordle_guess(self, ctx: discord.Interaction):
        await send_media(ctx, "https://cdn.discordapp.com/attachments/839100318893211669/1463529624368578730/james_doakes_sus.mp4?ex=697229ad&is=6970d82d&hm=2ebdf49d9883e596017095b265acda6b4bc533d055bc20bab93873c9e70e4eb7&")


    @app_commands.command(
        name="minecraft",
        description="I be placing blocks n shit, cuz im in fucking minecraft",
    )
    async def minecraft(self, ctx: discord.Interaction):
        gifs = [
            "https://cdn.discordapp.com/attachments/839100318893211669/1281936983135879262/minecraft.mp4?ex=66dd885a&is=66dc36da&hm=01e0ecc04e358363d36ee5c79fc6fe717b2b815844c31a6a6438d57a2b9b188e&",
            "https://cdn.discordapp.com/attachments/839100318893211669/1463529590134804633/minecraft_mmm_snapping_sounds.mp4?ex=697229a5&is=6970d825&hm=ed87b45c54a58b2c77d985636dd50e23186077ec11a09f2ca3516ba8e5ad048c&",
            "https://cdn.discordapp.com/attachments/839100318893211669/1463529650230792365/minecraft_seranade.mov?ex=697229b3&is=6970d833&hm=a2b6b22718a4cb5bb748371041ebb7f99d09fe1711eebf0baf0728cde39ee9f1&",
        ]
        await send_media(ctx, gifs)


    @app_commands.command(
        name="help",
        description="Gee you already know im obsessed with it *burp*, i cant get enough, back with another milk- ",
    )
    async def help(self, ctx: discord.Interaction):
        await send_media(ctx, "https://cdn.discordapp.com/attachments/839100318893211669/1310589750490562640/HEEEELP.mp4?ex=6745c552&is=674473d2&hm=86c7673380acaf4bea501ca6cd938ba70da9ed7aa783882fa4445ef98c02ba85&")

    @app_commands.command(
        name="im_losing_it",
        description="DU DU DU, babababaaaaa babababa baba baba baaa baba ba baaa baaa baba ba ba babababa bababa baba",
    )
    async def im_losing_it(self, ctx: discord.Interaction):
        await send_media(ctx, "https://cdn.discordapp.com/attachments/839100318893211669/1463529639015354451/im_losing_it.mp4?ex=697229b1&is=6970d831&hm=f196b15a2310458bfe65b3837b61092e600d6eef0d9fd2f39e4b09f372af9421&")


    @app_commands.command(
        name="wassup_beijing",
        description="Christian winnie the pooh cosplay",
    )
    async def wassup_beijing(self, ctx: discord.Interaction):
        await send_media(ctx, "https://cdn.discordapp.com/attachments/839100318893211669/1310925320014008340/wassup-beijing.mp4?ex=6746fdd8&is=6745ac58&hm=f3e680140b5238a1f6ec58b7c8ba95c7223e1fcc5246028dc7ba797be7d6f128&")

    @app_commands.command(
        name="gn_girl",
        description="*Rambunctious falling sounds*",
    )
    async def gn_girl(self, ctx: discord.Interaction):
        await send_media(ctx, "https://cdn.discordapp.com/attachments/839100318893211669/1310925339765248020/gn-girl.mp4?ex=6746fddc&is=6745ac5c&hm=b4168328e4f76d27e2649dc530bf33b69fcdc60c72a29f54d847bab35ac8b907&")

    @app_commands.command(
        name="dr_peppa",
        description="Epic dr pebba prank",
    )
    async def dr_peppa(self, ctx: discord.Interaction):
        await send_media(ctx, "https://cdn.discordapp.com/attachments/839100318893211669/1351897109263290479/dr-peppa.mp4?ex=67dc0bcb&is=67daba4b&hm=3c104e683e6274cd6dccb001ba942fc71dc446c127e3c107fff159b5b456b418&")

    @app_commands.command(
        name="sybau",
        description="man shut yo bitchass up",
    )
    async def sybau(self, ctx: discord.Interaction):
        await send_media(ctx, "https://cdn.discordapp.com/attachments/839100318893211669/1463529609092927634/sybau.mp4?ex=697229a9&is=6970d829&hm=9eee151906d8101b13006fee369d379c5db1f71ff11521bc2b28cf1da852c1cb&")

    @app_commands.command(
        name="game_pitch",
        description="ok hear me out",
    )
    async def game_pitch(self, ctx: discord.Interaction):
        await send_media(ctx, "https://cdn.discordapp.com/attachments/839100318893211669/1463529572115939454/games_pitch.mp4?ex=697229a1&is=6970d821&hm=d80a2a59907c67d132756addcfb51e251ba49104412afc0dc25453ce0a98d37a&")


    @app_commands.command(
        name="horse",
        description="is this real?",
    )
    async def at_horse_is_this_real(self, ctx: discord.Interaction):
        gifs = [
            "https://media.discordapp.net/attachments/1217933367849386004/1377728074438803566/AWARE.gif?ex=683a04c1&is=6838b341&hm=0a57f01e1253027e8a9b8c0bafd03cafe842f2f5a006f0e6cbf46611cf87ae50&=&width=704&height=704",
            "https://media.discordapp.net/attachments/1217933367849386004/1377728074849718272/horse-nod.gif?ex=683a04c1&is=6838b341&hm=88ae5035ea75b1c677bddda393f7610744e84eeb26005c4c86d4b0778c6458e5&=&width=264&height=469",
            "https://media.discordapp.net/attachments/1217933367849386004/1377728075369939106/horse-tongue.gif?ex=683a04c2&is=6838b342&hm=f6762c232599eb056b879c10a6e79a5e661fc02e28625159b6c35cac42d03ffe&=&width=440&height=548",
            "https://media.discordapp.net/attachments/1217933367849386004/1377728075843768481/joel.gif?ex=683a04c2&is=6838b342&hm=70236a47edeffc70a92e764c994e8f10029b4a6253dfbcdb8edc2951079a7852&=&width=528&height=528",
            "https://media.discordapp.net/attachments/1217933367849386004/1377728076233965628/mogged.gif?ex=683a04c2&is=6838b342&hm=abfe80050a9565f830eb5f609cb4cbfa5d363cf4544ec33e52d6ff392c0ee1e8&=&width=660&height=438",
            "https://media.discordapp.net/attachments/1217933367849386004/1377728076728762449/nop....gif?ex=683a04c2&is=6838b342&hm=6f87bf3e9a18d7c79c962a78bf126e8622a533b2a988160fc5a1d854af9b7c02&=&width=352&height=343",
            "https://media.discordapp.net/attachments/1217933367849386004/1377728077177688185/RUN.gif?ex=683a04c2&is=6838b342&hm=6fa81c547c0076b4e1b89d9b95d24d852c66364c17f00753e35e324d28901957&=&width=548&height=405",
            "https://media.discordapp.net/attachments/1217933367849386004/1377728077718884513/uhhhhh.gif?ex=683a04c2&is=6838b342&hm=a8feb2a95aa152981327b335197e9fd0bd65645bf6c1c0cc75015bcd5afb1b1e&=&width=310&height=548",
            "https://media.discordapp.net/attachments/1217933367849386004/1377728078360608778/yapyapyap.gif?ex=683a04c2&is=6838b342&hm=a9c96acfe2fe48f2da22273f329e0d33e85ab26afafac50b805ded7310aa3c09&=&width=411&height=411",
            "https://media.discordapp.net/attachments/1217933367849386004/1377728078788296774/yeeeeeesssss.gif?ex=683a04c2&is=6838b342&hm=1875126d84f1c2ea82c9a499e486ed3ba7faed0a8e6ed088298cdb448c92e8c6&=&width=310&height=548"
        ]
        await send_media(ctx, gifs)


async def setup(bot: Elgatron):
    await bot.add_cog(StimCommands(bot), guild=discord.Object(id=bot.guild_id))
