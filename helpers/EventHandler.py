import asyncio
import logging
import shutil

from dotmap import DotMap
from helpers.Enums import QueueStatus


class EventHandler:
    def __init__(
        self, modules: DotMap = None, loop: asyncio.AbstractEventLoop = None
    ) -> None:
        self.modules = modules
        self.loop = loop
        self.queues = DotMap(
            {
                "podcast": {
                    "queue": asyncio.Queue(),
                    "status": QueueStatus.IDLE,
                },
                "obs": {
                    "queue": asyncio.Queue(),
                    "status": QueueStatus.IDLE,
                },
            }
        )

    def handleEvent(self, event: str = None, **kwargs):
        eventHandler = "handle_" + event
        if hasattr(self, eventHandler):
            handler = getattr(self, eventHandler)
            handler(**kwargs)
        pass

    def handle_newTrack(
        self,
        artist: str = None,
        title: str = None,
        containsCoverArt: bool = False,
        *args,
        **kwargs,
    ):
        self.loop.call_soon_threadsafe(self.queues.obs.queue.put_nowait, 1)
        self.loop.call_soon_threadsafe(self.queues.podcast.queue.put_nowait, 1)
        asyncio.gather(
            self.handle_newTrack_task(
                self.queues.podcast, artist, title, containsCoverArt
            ),
            self.handle_newTrack_task(self.queues.obs, artist, title, containsCoverArt),
        )

    async def handle_newTrack_task(self, currentQueue, artist, title, containsCoverArt):
        while True:
            await currentQueue.queue.get()
            if not currentQueue.status:
                currentQueue.status = QueueStatus.PROCESSING
                logging.info(f"Handle new track:")
                logging.info(f"Artist: {artist} | Title: {title}")
                logging.info(f"Cover art: {containsCoverArt}")
                if not containsCoverArt:
                    self.copyFallbackImageToCoverFile()
                logging.info(f"{self.modules}")
                self.modules.obs.loop.run_until_complete(
                    self.modules.obs.module.eventUpdateSmallTrackInfoThenTriggerSlideAnimation(
                        artist, title
                    )
                )
                currentQueue.status = QueueStatus.IDLE
            currentQueue.queue.task_done()

    def copyFallbackImageToCoverFile(self):
        shutil.copy2(
            "external/djctl/record-vinyl-solid-light.png",
            "external/djctl/latest-cover-art.png",
        )
