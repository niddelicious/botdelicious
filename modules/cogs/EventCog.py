import logging
from twitchio.ext import commands


class EventCog(commands.Cog):
    def __init__(self):
        logging.debug(f"Adding event/cogs")

    @commands.command(name="lineup", aliases=["schedule", "times"])
    async def lineup(self, ctx: commands.Context):
        pass
