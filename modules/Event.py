import asyncio
import logging
import shutil

from helpers.AbstractModule import BotdeliciousModule
from helpers.Enums import ModuleStatus, QueueStatus


class EventModule(BotdeliciousModule):
    def __init__(self, parent=None, eventHandler=None):
        super().__init__(eventHandler=eventHandler)
        self.parent = parent

    def start(self):
        self.parent.eventHandler = self
        self.status = ModuleStatus.RUNNING

    def status(self):
        return self.status

    def stop(self):
        self.status = ModuleStatus.STOPPING
        self.loop.stop()
        self.status = ModuleStatus.IDLE

    async def run(self):
        logging.debug(f"Starting Event!")
        loopIteration = 1
        while True:
            logging.debug(f"Event loop: {loopIteration} {self.status}")
            self.checkLoopIsRunning()
            await asyncio.sleep(3)
            loopIteration += 1

    def checkLoopIsRunning(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logging.error(f"No running event loop!")
        else:
            logging.debug(f"Running event loop found: {loop}")

    def handleEvent(self, event: str = None, *args, **kwargs):
        logging.debug(f"Event received:")
        logging.debug(f"{args}")
        logging.debug(f"{kwargs}")
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
