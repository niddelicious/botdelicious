import asyncio
import logging
from pathlib import Path
import shutil
from dotmap import DotMap
from AsyncioThread import AsyncioThread
from Modules.BotdeliciousModule import BotdeliciousModule
from Helpers.Enums import ModuleStatus, TwinklyEffect, TwinklyPlaylist
from Helpers.SessionData import SessionData
from Modules.TwinklyModule import TwinklyModule
from Helpers.Utilities import Utilities


class EventModule(BotdeliciousModule):
    _event_queue = asyncio.Queue()
    _obs_instances = []
    _loop_sleep = 0
    _sd_module = None

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
    def set_loop_sleep(cls, sleep_time: int = 0):
        cls._loop_sleep = sleep_time

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
        logging.debug("Starting Event!")
        queue_logged = False
        while cls._status == ModuleStatus.RUNNING:
            if not cls._event_queue.empty():
                logging.debug(f"Event queue size: {cls._event_queue.qsize()}")
                queue_logged = False
                await cls.handle_event_queue()
            else:
                if not queue_logged:
                    logging.debug("Event queue is empty")
                    queue_logged = True
            await asyncio.sleep(cls._loop_sleep)
        while cls._status == ModuleStatus.STOPPING:
            logging.debug("Stopping event!")
            await asyncio.sleep(3)
        while cls._status == ModuleStatus.IDLE:
            logging.debug("Event stopped")
            await asyncio.sleep(3)

    @classmethod
    async def handle_event_queue(cls):
        logging.debug("Event queue not empty!")
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
            logging.error("No running event loop!")
        else:
            logging.debug(f"Running event loop found: {loop}")

    @classmethod
    async def queue_event(cls, event: str = None, *args, **kwargs):
        logging.debug("Event received:")
        logging.debug(f"event: {event}")
        logging.debug(f"args: {args}")
        logging.debug(f"kwargs: {kwargs}")
        item_to_queue = DotMap(
            {
                "event_type": event,
                "event_data": {**kwargs},
                "additional_data": {*args},
            }
        )
        await cls._event_queue.put(item_to_queue)

    @classmethod
    async def direct_event(cls, event: str = None, *args, **kwargs):
        direct_data = DotMap(
            {
                "event_type": event,
                "event_data": {**kwargs},
                "additional_data": {*args},
            }
        )
        direct_type_handler_method = "direct_" + direct_data.event_type
        if hasattr(cls, direct_type_handler_method):
            handler = getattr(cls, direct_type_handler_method)
            await handler(item_data=direct_data.event_data)

    @classmethod
    async def handle_new_track(cls, item_data=None, *args, **kwargs):
        logging.debug("Handle new track:")
        logging.debug(f"Artist: {item_data.artist} | Title: {item_data.title}")
        logging.debug(f"Cover art: {item_data.contains_cover_art}")

        if not item_data.contains_cover_art:
            Utilities.copy_fallback_image_to_cover_file()

        logging.debug("Storing new track in session data")
        SessionData.set_current_track(artist=item_data.artist, title=item_data.title)
        logging.debug("Updating track stat list")
        await asyncio.gather(
            *[instance.event_update_stats() for instance in cls._obs_instances]
        )

    @classmethod
    def update_obs_instances(cls, *args, **kwargs):
        from Controllers.ModulesController import ModulesController
        from Modules.OBSModule import OBSModule

        cls._obs_instances = []
        for instance in OBSModule.get_running_instances():
            cls._obs_instances.append(
                ModulesController.get_module(module_name=instance)
            )

    @classmethod
    def update_sd_module(cls, module=None, *args, **kwargs):
        from Modules.StableDiffusionModule import StableDiffusionModule

        cls._sd_module = module

    @classmethod
    async def handle_show_small_track_id(cls, *args, **kwargs):
        logging.debug("Show small track id:")
        await asyncio.gather(
            *[instance.event_new_track() for instance in cls._obs_instances]
        )

    @classmethod
    async def handle_show_big_track_id(cls, *args, **kwargs):
        logging.debug("Show big track id:")
        await asyncio.gather(
            *[instance.event_track_id() for instance in cls._obs_instances]
        )

    @classmethod
    async def handle_shoutout(cls, item_data=None, *args, **kwargs):
        logging.debug("Show shoutout:")
        await asyncio.gather(
            *[
                instance.event_shoutout(
                    username=item_data.username,
                    message=item_data.message,
                    avatar_url=item_data.avatar_url,
                )
                for instance in cls._obs_instances
            ]
        )

    @classmethod
    async def handle_fire(cls, *args, **kwargs):
        logging.debug("Fire!")
        await asyncio.gather(
            *[instance.event_fire() for instance in cls._obs_instances],
            TwinklyModule.playlist(TwinklyPlaylist.FIRE, 10),
        )

    @classmethod
    async def handle_tune(cls, *args, **kwargs):
        logging.debug("Tune!")
        await asyncio.gather(
            *[instance.event_tune() for instance in cls._obs_instances],
            TwinklyModule.playlist(TwinklyPlaylist.RAINBOW_WAVES, 10),
        )

    @classmethod
    async def handle_new_follower(cls, item_data=None, *args, **kwargs):
        logging.debug("New follower")
        await asyncio.gather(
            *[
                instance.event_new_follower(
                    username=item_data.username,
                    avatar_url=item_data.avatar_url or None,
                )
                for instance in cls._obs_instances
            ],
            TwinklyModule.playlist(TwinklyPlaylist.LOVE, 8),
        )

    @classmethod
    async def handle_raid(cls, item_data=None, *args, **kwargs):
        logging.debug("Raid!")
        await asyncio.gather(
            *[
                instance.event_raid(
                    name=item_data.name,
                    count=item_data.count,
                    avatar_url=item_data.avatar_url or None,
                )
                for instance in cls._obs_instances
            ],
            TwinklyModule.playlist(TwinklyPlaylist.GREEN_WAVES, 8),
        )

    @classmethod
    async def handle_moderator(cls, item_data=None, *args, **kwargs):
        logging.debug("Moderator check-in")
        await asyncio.gather(
            *[
                instance.event_moderator(moderator=item_data.moderator)
                for instance in cls._obs_instances
            ]
        )

    @classmethod
    async def handle_vip(cls, item_data=None, *args, **kwargs):
        logging.debug("VIP check-in")
        await asyncio.gather(
            *[instance.event_vip(vip=item_data.vip) for instance in cls._obs_instances]
        )

    @classmethod
    async def handle_chatter(cls, item_data=None, *args, **kwargs):
        logging.debug("Chatter check-in")
        await asyncio.gather(
            *[
                instance.event_chatter(chatter=item_data.chatter)
                for instance in cls._obs_instances
            ]
        )

    @classmethod
    async def handle_change_video(cls, item_data=None, *args, **kwargs):
        logging.debug("Change video")
        await asyncio.gather(
            *[
                instance.event_change_video(video=item_data.video)
                for instance in cls._obs_instances
            ]
        )

    @classmethod
    async def handle_switch_scene(cls, item_data=None, *args, **kwargs):
        logging.debug("Switch scene")
        await asyncio.gather(
            *[
                instance.switch_scene(scene_name=item_data.scene_name)
                for instance in cls._obs_instances
            ]
        )

    @classmethod
    async def handle_new_message(cls, *args, **kwargs):
        logging.debug("Updating messages")
        SessionData.add_comment()
        await asyncio.gather(
            *[instance.event_update_stats() for instance in cls._obs_instances]
        )

    @classmethod
    async def handle_sync_recording(cls, item_data=None, *args, **kwargs):
        logging.debug("Synchronizing recording state")
        await asyncio.gather(
            *[
                instance.sync_record_toggle(record_status=item_data.record_status)
                for instance in cls._obs_instances
            ]
        )

    @classmethod
    async def handle_sync_scene(cls, item_data=None, *args, **kwargs):
        logging.debug("Synchronizing scene switch")
        await asyncio.gather(
            *[
                instance.sync_scene_switch(event_data=item_data.event_data)
                for instance in cls._obs_instances
            ]
        )

    @classmethod
    async def handle_show_generated_image(cls, item_data=None, *args, **kwargs):
        logging.debug("Showing generated image")
        await asyncio.gather(
            *[
                instance.show_generated_image(
                    url=item_data.url,
                    author=item_data.author,
                    prompt=item_data.prompt,
                )
                for instance in cls._obs_instances
            ]
        )

    @classmethod
    async def handle_sd_generate_image(cls, item_data=None, *args, **kwargs):
        logging.debug("SD start image")
        await asyncio.gather(
            cls._sd_module.generate_image(
                item_data.prompt, item_data.style, item_data.author
            ),
            *[
                instance.sd_start(
                    prompt=item_data.prompt,
                    author=item_data.author,
                    style=item_data.style,
                )
                for instance in cls._obs_instances
            ],
        )
        await asyncio.gather(
            *[instance.sd_show(item_data.author) for instance in cls._obs_instances]
        )

    @classmethod
    async def direct_sd_progress(cls, item_data=None, *args, **kwargs):
        logging.debug("SD progress_update")
        await asyncio.gather(
            *[
                instance.sd_progress(
                    eta=item_data.eta,
                    percent=item_data.percent,
                    steps=item_data.steps,
                )
                for instance in cls._obs_instances
            ],
        )

    @classmethod
    async def handle_kofi(cls, item_data=None, *args, **kwargs):
        logging.debug("Ko-fi donation!")
        logging.debug(f"Item data: {item_data}")
        await asyncio.gather(
            *[
                instance.kofi(
                    name=item_data.from_name,
                    amount=item_data.amount,
                    currency=item_data.currency,
                    message=item_data.message,
                )
                for instance in cls._obs_instances
            ],
            TwinklyModule.playlist(TwinklyPlaylist.I_LOVE_YOU, 10),
        )

    @classmethod
    async def direct_trip_balls(cls, item_data=None, *args, **kwargs):
        logging.debug("Trip balls")
        await asyncio.gather(
            *[instance.trip_balls() for instance in cls._obs_instances],
        )

    @classmethod
    async def direct_saturate(cls, item_data=None, *args, **kwargs):
        logging.debug("Saturate")
        await asyncio.gather(
            *[instance.saturate() for instance in cls._obs_instances],
        )

    @classmethod
    async def direct_desaturate(cls, item_data=None, *args, **kwargs):
        logging.debug("Desaturate")
        await asyncio.gather(
            *[instance.desaturate() for instance in cls._obs_instances],
        )
