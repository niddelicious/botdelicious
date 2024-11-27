import logging
from twitchio.ext import commands

from Modules.AnthropicModule import AnthropicModule


class EventCog(commands.Cog):
    def __init__(self):
        logging.debug(f"Adding event/cogs")

    @commands.command(name="lineup", aliases=["schedule", "times"])
    async def lineup(self, ctx: commands.Context):
        pass
        return
        lineup = "This is the Summer Shindig 2024 Raid Train, and the upcoming streamers are: @Hallucyn8 4pm CET, @DJEgo07 6pm CET, and @loft214 8pm CET, with more than a dozen after that. Full schedule: https://raidpal.com/en/event/summer-shindig-2024"
        reply = await AnthropicModule.pa_intepretor(
            content=lineup, author="niddelicious"
        )
        await ctx.send(reply)
