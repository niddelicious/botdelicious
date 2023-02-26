import asyncio
import logging
import shutil
from dotmap import DotMap
from helpers.AbstractModule import BotdeliciousModule
from helpers.Enums import ModuleStatus, QueueStatus


class EventModule(BotdeliciousModule):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.eventQueue = asyncio.Queue()

    def start(self):
        self.parent.setEventHandler(self)
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
            if not self.eventQueue.empty():
                await self.handleEventQueue()
            await asyncio.sleep(1)
            loopIteration += 1

    async def handleEventQueue(self):
        event_item = await self.eventQueue.get()
        eventTypeHandlerMethod = "handle_" + event_item.eventType
        if hasattr(self, eventTypeHandlerMethod):
            handler = getattr(self, eventTypeHandlerMethod)
            await handler(itemData=event_item.eventData)
        self.eventQueue.task_done()

    def checkLoopIsRunning(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logging.error(f"No running event loop!")
        else:
            logging.debug(f"Running event loop found: {loop}")

    async def queueEvent(self, event: str = None, *args, **kwargs):
        logging.debug(f"Event received:")
        logging.debug(f"{args}")
        logging.debug(f"{kwargs}")
        itemToQueue = DotMap(
            {
                "eventType": event,
                "eventData": {**kwargs},
            }
        )
        await self.eventQueue.put(itemToQueue)

    async def handle_newTrack(self, itemData=None):
        logging.info(f"Handle new track:")
        logging.info(f"Artist: {itemData.artist} | Title: {itemData.title}")
        logging.info(f"Cover art: {itemData.containsCoverArt}")
        if not itemData.containsCoverArt:
            self.copyFallbackImageToCoverFile()
        await self.parent.modules.podcast.module.eventTriggerSlideAnimationThenUpdateSmallTrackInfo(
            itemData.artist, itemData.title
        )
        await self.parent.modules.obs.module.eventUpdateSmallTrackInfoThenTriggerSlideAnimation(
            itemData.artist, itemData.title
        )

    def copyFallbackImageToCoverFile(self):
        shutil.copy2(
            "external/djctl/record-vinyl-solid-light.png",
            "external/djctl/latest-cover-art.png",
        )
