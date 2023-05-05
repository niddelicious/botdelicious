import logging
import random
import yaml
from twitchio.ext import commands
from Helpers.Enums import TwinklyEffect, TwinklyReact

from Helpers.SessionData import SessionData
from Helpers.Timer import Timer
from Helpers.Utilities import Utilities
from Modules.EventModule import EventModule
from Modules.OpenaiModule import OpenaiModule
from Modules.TwinklyModule import TwinklyModule


class TimersCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        logging.debug(f"Adding timers/cogs")
        self.bot = bot

    @commands.command(
        name="remaining",
        aliases=["timeremaining", "remainingtimers", "remainingtime"],
    )
    async def remaining(self, ctx: commands.Context):
        timers = Timer.timers()
        timers_message: str = "Timers | "
        if timers:
            for timer in timers:
                timers_message += f"{timer.name}: {timer.time_left()} | "
        else:
            timers_message += "None"

        await ctx.send(f"{timers_message}")
