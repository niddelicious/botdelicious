import logging
from twitchio.ext import commands

from Modules.OpenaiModule import OpenaiModule


class EventCog(commands.Cog):
    def __init__(self):
        logging.debug(f"Adding event/cogs")

    @commands.command(name="lineup", aliases=["schedule", "times"])
    async def lineup(self, ctx: commands.Context):
        pass
        return None
        lineup = "Remaining lineup of streamers in this raid train and times in CET: 09:00 @dj_martin_lune 11:00 @DanjunaDJ 13:00 @Dieselmax 15:00 @adrienLT_DJ 17:00 @JostonMusic 19:00 @BendyBusDriver 21:00 @tkkttony"
        reply = await OpenaiModule.pa_intepretor(
                content=lineup, author="niddelicious"
            )
        await ctx.send(reply)

