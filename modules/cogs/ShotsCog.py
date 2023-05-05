import asyncio
import logging
from twitchio.ext import commands

from Helpers.Timer import Timer


class ShotsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        logging.debug(f"Adding shots/cogs")
        self.bot = bot
        self._bar_open = False
        self._shots = 0
        self._shot_requested = False
        self._shot_taken = False
        self._shot_accepted = False
        self._drinkers = []
        self._drunkards = []
        self._knocks = 0

    @commands.command(name="openbar", aliases=["opentab", "baropen"])
    async def openbar(self, ctx: commands.Context):
        if ctx.author.is_broadcaster and not self._bar_open:
            self._bar_open = True
            await ctx.send(f"🥃 The bar is now open! 🥃")

    @commands.command(name="closebar", aliases=["closetab", "barclose"])
    async def closebar(self, ctx: commands.Context):
        if ctx.author.is_broadcaster and self._bar_open:
            self._bar_open = False
            await ctx.send(f"🚪 The bar is now closed 🔐")

    @commands.command(
        name="remaining",
        aliases=["timeremaining", "remainingtimers", "remainingtime"],
    )
    async def remaining(self, ctx: commands.Context):
        timers = Timer.timers()
        timers_message: str = "Timers | "
        if timers:
            for timer in timers:
                timers_message += f"{timer['name']}: {timer['time_left']} | "
        else:
            timers_message += "None"

        await ctx.send(f"{timers_message}")

    @commands.command(name="shot", aliases=["shots", "drink", "drinks"])
    async def shot(self, ctx: commands.Context):
        if not self._bar_open:
            if self._knocks >= 3:
                await ctx.send(
                    f"@{ctx.author.name} Listen, the bar isn't open. Have some water 🚰 Get help. Call AA! 🚑"
                )
                self._knocks = 0
                return
            else:
                self._knocks += 1
                return
        if self._shot_requested:
            await ctx.send(
                f"Hold your horses, @{ctx.author.name}! The last challenge from @{self._shot_requested} has not been answered yet!"
            )
        elif self._shot_taken:
            await ctx.send(
                f"Let's give the last 🥃 time to sink in, huh @{ctx.author.name}?"
            )
        elif self._shot_accepted:
            await ctx.send(
                f"@{ctx.author.name} We're doing it! 🥃 Get in on it!"
            )
        else:
            self._shot_requested = ctx.author.name
            await ctx.send(
                f"{'🥃 ' * self._shots}@{ctx.author.name} has requested a shot! 🥃 Will it be !accepted ✅ or !denied ⛔?"
            )

    @commands.command(name="deny", aliases=["denied", "nope", "no"])
    async def deny(self, ctx: commands.Context):
        if not self._shot_requested:
            await ctx.send(
                f"Sure @{ctx.author.name}, but there is no challenge to deny. 👎 What's with the negativity? 👎"
            )
            return
        if ctx.author.is_broadcaster:
            await ctx.send(
                f"🙅‍♂️ @{ctx.author.name} has denied the challenge! ⛔"
            )
            self._shot_requested = False
            if self._drinkers:
                await ctx.send(
                    f"Well, cheers anyway 🥃 {' '.join([f'@{name}' for name in self._drinkers])} 🥃"
                )
                self._drinkers = []
            await Timer.start("Wuss", 30, self._wuss, ctx=ctx)
        else:
            await ctx.send(f"🙅‍♂️ @{ctx.author.name} is out! ⛔")

    async def _wuss(self, ctx: commands.Context):
        await ctx.send(f"@{ctx.author.name} Wuss! 🤡")

    @commands.command(name="accept", aliases=["accepted", "yes", "yep"])
    async def accept(self, ctx: commands.Context):
        if not self._shot_requested:
            await ctx.send(
                f"Sure @{ctx.author.name}, but there is no challenge to accept. 🥴 So eager, you drunkard 🥴"
            )
            return
        if ctx.author.is_broadcaster:
            self._shot_accepted = True
            self._shot_requested = False
            self.add_drinker(ctx.author.name)
            await ctx.send(
                f"✅ ACCEPTED! @{ctx.author.name} IS IN! LESSGO! 🥃 Shots all around! 🥃 20 seconds!"
            )
            await asyncio.sleep(10)
            await ctx.send(f"🥃 10 seconds")
            await asyncio.sleep(5)
            await ctx.send(f"🥃 5 seconds")
            await asyncio.sleep(2)
            await ctx.send(f"🥃 3")
            await asyncio.sleep(1)
            await ctx.send(f"🥃 2")
            await asyncio.sleep(1)
            await ctx.send(f"🥃 1")
            await asyncio.sleep(1)
            await ctx.send(
                f"🍻🥃 CHEERS! 🥃 🍻{' '.join([f'@{name} 🍻' for name in self._drinkers])}"
            )
            self._shots += 1
            self._shot_taken = True
            self.move_drinkers()
            await Timer.start(
                "Reopen the bar", 15 * 60, self._reopen_the_bar, ctx=ctx
            )
        else:
            if self.add_drinker(ctx.author.name):
                await ctx.send(f"✅ {ctx.author.name} is in! 🍻")
            else:
                await ctx.send(f"{ctx.author.name} We know, we know! 🍻")

    def add_drunkard(self, name: str):
        if name not in self._drunkards:
            self._drunkards.append(name)

    def add_drinker(self, name: str):
        if name not in self._drinkers:
            self._drinkers.append(name)
            return True
        else:
            return False

    def move_drinkers(self):
        for drinker in self._drinkers:
            self.add_drunkard(drinker)
        self._drinkers = []

    async def _reopen_the_bar(self, ctx: commands.Context):
        self._shot_taken = False
        await ctx.send(f"🥃 Bar is open again! 🥃")

    @commands.command(
        name="drunkars", aliases=["drunkards", "drunkies", "drinkers"]
    )
    async def drunkars(self, ctx: commands.Context):
        if self._drunkards:
            await ctx.send(f"Drunkars so far: {' 🥃 '.join(self._drunkards)}")
        else:
            await ctx.send(f"This is a dry zone 🚰")

    @commands.command(name="timertest")
    async def timertest(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            await ctx.send(f"Test timer started!")
            await Timer.start("Test", 3, self._test, ctx=ctx)

    @commands.command(name="canceltest")
    async def canceltest(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            await ctx.send(f"Cancel timer started!")
            await Timer.start("Cancel test", 10, self._test, ctx=ctx)
            await asyncio.sleep(2)
            Timer.cancel("Cancel test")
            await ctx.send(f"Cancel timer canceled!")

    async def _test(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            await ctx.send(f"Test timer done!")

    @commands.command(
        name="reopenbar", aliases=["reopen", "thirsty", "alcoholic"]
    )
    async def reopenbar(self, ctx: commands.Context):
        if not ctx.author.is_broadcaster:
            return
        if self._shot_taken:
            await ctx.send(f"🔓 I'm not gonna carry you home 🥃")
            Timer.cancel("Reopen the bar")
            self._shot_taken = False
        elif self._bar_open:
            await ctx.send(
                f"@{ctx.author.name} It's already open 🥃 Maybe you just shouldn't have more? 🥴 "
            )
