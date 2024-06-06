import asyncio
from twitchio.ext import commands
from Helpers.Timer import Timer
from Modules.OpenaiModule import OpenaiModule
from Controllers.ConfigController import ConfigController


class PublicAnnouncementCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self._pa_enabled = False
        self._initial_delay = 60 * 5  # 5 minutes
        self._message_delay = 60 * 6  # 6 minutes
        self._message_index = 0
        twitch_config = ConfigController.get_config_file("twitch_channel.yaml")
        self._public_announcements = twitch_config.commands.pa
        if isinstance(twitch_config.commands.delay, int):
            self._message_delay = 60 * twitch_config.commands.delay
        asyncio.create_task(self.pa_autostart())

    def get_announcement(self):
        if self._message_index >= len(self._public_announcements):
            self._message_index = 0
        announcement = self._public_announcements[self._message_index]
        self._message_index += 1
        return announcement

    async def pa_autostart(self):
        self._pa_enabled = True
        await Timer.start(
            "public_announcement",
            self._initial_delay,
            self._public_announcement,
        )

    @commands.command(
        name="unpa",
        aliases=[
            "unpublic_announcement",
            "stop_pa",
            "stop_public_announcement",
        ],
    )
    async def unpa(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            self._pa_enabled = False
            Timer.cancel("public_announcement")

    async def _public_announcement(self):
        while self._pa_enabled:
            reply = await OpenaiModule.pa_intepretor(
                content=self.get_announcement(), author="niddelicious"
            )
            await self.bot.say_everywhere(reply)
            await asyncio.sleep(self._message_delay)
