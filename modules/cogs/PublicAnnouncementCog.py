import asyncio
from twitchio.ext import commands
from Helpers.Timer import Timer
from Modules.OpenaiModule import OpenaiModule


class PublicAnnouncementCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self._pa_enabled = False
        self._initial_delay = 60 * 5  # 5 minutes
        self._message_delay = 60 * 6  # 6 minutes
        self._message_index = 0
        self._public_announcements = [
            f"Available commands in chat are: !id (displays track id) !so (shouts out another streamer) !hug (to hug another chatter) !lurk (to announce your lurk) !lick (to lick another chatter) !fire (to light flames for this fire track) !tune (declaring this track to be an absolute tune) !video (changing the video in the background) !lights (to change the lights) !imagine (to generate an image using ai) !shots (to request a shot together with the streamer)",
            f"Commands are all free and open to everyone.",
            f"This channel is unaffiliated so that all viewers can watch it ad-free.",
            f"Streams are archived on YouTube at https://www.youtube.com/@niddelicious, unless they're copyright blocked there.",
            f"Music-only MP3s of all streams are archived at https://nidde.nu",
            f"AI images that are generated with !imagine command will later be displayed at https://nidde.nu/gallery",
            f"Thank everyone for being here. I appreciate everyone, whether you're lurking or chatting.",
        ]
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
