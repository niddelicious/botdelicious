import asyncio
import logging
import shutil
from dotmap import DotMap
from AsyncioThread import AsyncioThread
from helpers.AbstractModule import BotdeliciousModule
from helpers.Enums import ModuleStatus
from helpers.SessionData import SessionData


class EventModule(BotdeliciousModule):
    _event_queue = asyncio.Queue()
    _obs_instances = []

    def __init__(self):
        super().__init__()

    async def start(self):
        AsyncioThread.run_coroutine(self.run())
        self.set_status(ModuleStatus.RUNNING)

    def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        AsyncioThread.stop_loop()
        self.set_status(ModuleStatus.IDLE)

    @classmethod
    async def get_event_queue(cls):
        return cls._event_queue

    @classmethod
    async def event_queue_is_empty(cls):
        return cls._event_queue.empty()

    @classmethod
    async def add_to_event_queue(cls, data):
        await cls._event_queue.put(data)

    async def run(cls):
        logging.debug(f"Starting Event!")
        while cls._status == ModuleStatus.RUNNING:
            if not cls._event_queue.empty():
                await cls.handle_event_queue()
            else:
                logging.debug(f"Event queue is empty")
            await asyncio.sleep(2)
        while cls._status == ModuleStatus.STOPPING:
            logging.DEBUG(f"Stopping event!")
            await asyncio.sleep(3)
        while cls._status == ModuleStatus.IDLE:
            logging.debug(f"Event stopped")
            await asyncio.sleep(3)

    @classmethod
    async def handle_event_queue(cls):
        logging.debug(f"Event queue not empty!")
        event_item = await cls._event_queue.get()
        logging.debug(f"{event_item}")
        event_type_handler_method = "handle_" + event_item.event_type
        if hasattr(cls, event_type_handler_method):
            handler = getattr(cls, event_type_handler_method)
            await handler(item_data=event_item.event_data)
        cls._event_queue.task_done()

    def checkLoopIsRunning(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logging.error(f"No running event loop!")
        else:
            logging.debug(f"Running event loop found: {loop}")

    @classmethod
    async def queue_event(cls, event: str = None, *args, **kwargs):
        logging.debug(f"Event received:")
        logging.debug(f"{event}")
        logging.debug(f"{args}")
        logging.debug(f"{kwargs}")
        item_to_queue = DotMap(
            {
                "event_type": event,
                "event_data": {**kwargs},
                "additional_data": {*args},
            }
        )
        await cls._event_queue.put(item_to_queue)

    @classmethod
    async def handle_new_track(cls, item_data=None, *args, **kwargs):
        logging.debug(f"Handle new track:")
        logging.debug(f"Artist: {item_data.artist} | Title: {item_data.title}")
        logging.debug(f"Cover art: {item_data.contains_cover_art}")

        if not item_data.contains_cover_art:
            cls._copy_fallback_image_to_cover_file()

        SessionData.set_current_track(
            {"artist": item_data.artist, "title": item_data.title}
        )

    def obs_event(func, *args, **kwargs):
        async def wrapper(self, *args, **kwargs):
            EventModule.update_obs_instances()
            await func(self, *args, **kwargs)

        return wrapper

    @classmethod
    def update_obs_instances(cls, *args, **kwargs):
        from helpers.ModulesManager import ModulesManager
        from modules.OBS import OBSModule

        cls._obs_instances = []
        for instance in OBSModule.get_running_instances():
            cls._obs_instances.append(
                ModulesManager.get_module(module_name=instance)
            )

    @classmethod
    @obs_event
    async def handle_show_small_track_id(cls, *args, **kwargs):
        logging.debug(f"Show small track id:")
        await asyncio.gather(
            *[
                instance.eventUpdateSmallTrackInfoThenTriggerSlideAnimation()
                for instance in cls._obs_instances
            ]
        )

    @classmethod
    @obs_event
    async def handle_show_big_track_id(cls, *args, **kwargs):
        logging.debug(f"Show big track id:")
        await asyncio.gather(
            *[
                instance.eventUpdateTrackInfoThenTriggerBigSlideAnimation()
                for instance in cls._obs_instances
            ]
        )

    @classmethod
    @obs_event
    async def handle_shoutout(cls, item_data=None, *args, **kwargs):
        logging.debug(f"Show shoutout:")
        await asyncio.gather(
            *[
                instance.eventUpdateShoutoutTextThenTriggerSlideAnimation(
                    username=item_data.username,
                    message=item_data.message,
                    avatar_url=item_data.avatar_url,
                )
                for instance in cls._obs_instances
            ]
        )

    @staticmethod
    def _copy_fallback_image_to_cover_file():
        shutil.copy2(
            "external/djctl/record-vinyl-solid-light.png",
            "external/djctl/latest-cover-art.png",
        )
