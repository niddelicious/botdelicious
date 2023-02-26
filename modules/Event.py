import asyncio
import logging
import shutil
from dotmap import DotMap
from AsyncioThread import AsyncioThread
from helpers.AbstractModule import BotdeliciousModule
from helpers.Enums import ModuleStatus, QueueStatus


class EventModule(BotdeliciousModule):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.eventQueue = asyncio.Queue()
        self.moduleStatus = ModuleStatus.IDLE

    def start(self):
        self.parent.setEventHandler(self)
        self.moduleStatus = ModuleStatus.RUNNING

    def status(self):
        return self.moduleStatus

    def stop(self):
        self.moduleStatus = ModuleStatus.STOPPING
        self.parent.stop_asyncio_thread()
        self.moduleStatus = ModuleStatus.IDLE

    async def run(self):
        logging.debug(f"Starting Event!")
        while self.moduleStatus == ModuleStatus.RUNNING:
            if not self.eventQueue.empty():
                await self.handleEventQueue()
            await asyncio.sleep(0)
        while self.moduleStatus == ModuleStatus.STOPPING:
            logging.DEBUG(f"Stopping event!")
            await asyncio.sleep(3)
        while self.moduleStatus == ModuleStatus.IDLE:
            logging.debug(f"Event stopped")
            await asyncio.sleep(3)

    async def handleEventQueue(self):
        logging.debug(f"handleEventQueue")
        event_item = await self.eventQueue.get()
        logging.debug(f"{event_item}")
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
        logging.debug(f"Handle new track:")
        logging.debug(f"Artist: {itemData.artist} | Title: {itemData.title}")
        logging.debug(f"Cover art: {itemData.containsCoverArt}")
        if not itemData.containsCoverArt:
            self.copyFallbackImageToCoverFile()
        await asyncio.gather(
            self.parent.modules.podcast.module.eventTriggerSlideAnimationThenUpdateSmallTrackInfo(
                itemData.artist, itemData.title
            ),
            self.parent.modules.obs.module.eventUpdateSmallTrackInfoThenTriggerSlideAnimation(
                itemData.artist, itemData.title
            ),
        )

    def copyFallbackImageToCoverFile(self):
        shutil.copy2(
            "external/djctl/record-vinyl-solid-light.png",
            "external/djctl/latest-cover-art.png",
        )
