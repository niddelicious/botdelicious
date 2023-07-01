import asyncio
from twitchio.ext import commands
from Helpers.Timer import Timer
from Modules.OpenaiModule import OpenaiModule


class CharityCog(commands.Cog):
    def __init__(self) -> None:
        super().__init__()
        self._charity_enabled = False
        self._message_delay = 60 * 5  # 5 minutes
        self._charity_message = """
        Today we are raising
        money for the Lumpy Lizard, Reptile, Poultry, and Exotics Rescue, based in Edna,
        Texas. Right now her animals are struggling under the hot Texas sun. We are raising
        money to better the conditions of their habitats and cover veterinary costs. This
        is their Facebook URL http://www.facebook.com/lumpylizardrescue
        Here is the donation link https://www.twitch.tv/charity/auntiesassquats
        """

    @commands.command(
        name="charity", aliases=["fundraiser", "donate", "donation", "cause"]
    )
    async def charity(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            self._charity_enabled = True
            await Timer.start("charity", 1, self._puplic_announcement, ctx=ctx)
        else:
            static_message = f"""
            💖 Thank you for showing interest, {ctx.author.name}! 🌟
            Use the link https://www.twitch.tv/charity/auntiesassquats to donate 💰
            And use the link http://www.facebook.com/lumpylizardrescue to read more about Lumpy Lizards 🦎
            """
            await ctx.send(static_message)

    @commands.command(
        name="uncharity", aliases=["unfundraiser", "undonate", "uncause"]
    )
    async def uncharity(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            self._charity_enabled = False
            Timer.cancel("charity")

    async def _puplic_announcement(self, ctx: commands.Context):
        while self._charity_enabled:
            reply = await OpenaiModule.pa_intepretor(
                content=self._charity_message, author=ctx.author.name
            )
            await ctx.send(reply)
            await asyncio.sleep(self._message_delay)
