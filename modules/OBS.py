import asyncio
import logging
from dotmap import DotMap
import simpleobsws
from AsyncioThread import AsyncioThread

from helpers.AbstractModule import BotdeliciousModule
from helpers.ConfigManager import ConfigManager
from helpers.Enums import ModuleStatus
from helpers.Enums import ModuleRole
from helpers.SessionData import SessionData
from modules.Event import EventModule
from helpers.Dataclasses import OBSText


class OBSModule(BotdeliciousModule):
    _running_instances = []
    _constants = DotMap(
        {
            "setlist_line_height": 40,
            "header_spacing": 10,
            "item_spacing": 20,
        }
    )
    _item_sizes = DotMap({"setlist": 0})

    def __init__(self, name: str = "obs") -> None:
        super().__init__()
        self._name = name
        self._role = ModuleRole.FOLLOWER
        self.config = None
        self._status = ModuleStatus.IDLE
        self._scenes = []
        self._inputs = []
        self._sources = self._inputs

    async def start(self):
        self.set_status(ModuleStatus.RUNNING)
        self.config = getattr(ConfigManager._config, self._name)
        parameters = simpleobsws.IdentificationParameters()
        parameters.eventSubscriptions = (1 << 0) | (1 << 2) | (1 << 6)
        self.ws = simpleobsws.WebSocketClient(
            url=f"ws://{self.config.ip}:{self.config.port}",
            password=self.config.password,
            identification_parameters=parameters,
        )
        self._role = (
            ModuleRole.LEADER if self.config.callbacks else ModuleRole.FOLLOWER
        )
        await self.connect()
        self.add_running_instance(self._name)
        await asyncio.gather(
            self.call_update_text(
                input_name="Small track artist",
                text=SessionData.current_artist(),
            ),
            self.call_update_text(
                input_name="Small track title",
                text=SessionData.current_title(),
            ),
        )
        if self._name == "twitch":
            asyncio.gather(
                self.call_update_text(
                    input_name="Big track artist",
                    text=SessionData.current_artist(),
                ),
                self.call_update_text(
                    input_name="Big track title",
                    text=SessionData.current_title(),
                ),
                self.event_update_stats(),
            )

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        await self.disconnect()
        self.remove_running_instance(self._name)
        self.set_status(ModuleStatus.IDLE)

    def status(self):
        return self.get_status()

    def get_status(self):
        return self._status

    def set_status(self, new_status: ModuleStatus):
        self._status = new_status

    async def gather_instance_data(self):
        request = simpleobsws.Request("GetSceneList")
        ret = await self.call(type="Gather scenes", request=request)
        for scene in ret["scenes"]:
            self._scenes.append(scene["sceneName"])

        request = simpleobsws.Request("GetInputList")
        ret = await self.call(type="Gather inputs", request=request)
        for source in ret["inputs"]:
            self._inputs.append(source["inputName"])

    def check_obs_sources(func):
        def wrapper(self, *args, **kwargs):
            relevant_kwargs = {
                name: value
                for name, value in kwargs.items()
                if any(word in name for word in ("source", "scene", "input"))
            }
            for kwarg_name, kwarg_value in relevant_kwargs.items():
                collection_name = f"_{kwarg_name.split('_')[0]}s"
                collection = getattr(self, collection_name, [])
                if kwarg_value not in collection:
                    logging.debug(f"{self._name} is skipping {kwarg_value}")
            return func(self, *args, **kwargs)

        return wrapper

    @classmethod
    def get_running_instances(cls):
        return cls._running_instances

    @classmethod
    def add_running_instance(cls, instance_name: str):
        if instance_name not in cls._running_instances:
            cls._running_instances.append(instance_name)

    @classmethod
    def remove_running_instance(cls, instance_name: str):
        if instance_name in cls._running_instances:
            cls._running_instances.remove(instance_name)

    async def connect(self, *args, **kwargs):
        logging.info(f"Connecting to {self._name}...")
        try:
            await self.ws.connect()
            await self.ws.wait_until_identified()
        except ConnectionError:
            logging.warn(f"Could not connect to {self._name}")
            return
        if self._role == ModuleRole.LEADER:
            self.ws.register_event_callback(self.on_event)
            self.ws.register_event_callback(
                self.on_scene_switched, "CurrentProgramSceneChanged"
            )
            self.ws.register_event_callback(
                self.on_stream_toggled, "StreamStateChanged"
            )
            self.ws.register_event_callback(
                self.on_record_toggled, "RecordStateChanged"
            )
            await self.event_clear_credits()

    async def disconnect(self):
        logging.info(f"Disconnecting from {self._name}")
        await self.ws.disconnect()

    async def call(
        self,
        type: str = "Call",
        request: simpleobsws.Request = None,
        *args,
        **kwargs,
    ):
        ret = await self.ws.call(request)  # Perform the request

        if ret.ok():  # Check if the request succeeded
            logging.debug(f"|{self._name}| {type} succeeded!")
            logging.debug(f"Response data: {ret.responseData}")
            return ret.responseData
        else:
            logging.warn(f"|{self._name}| {type} failed!")
            logging.warn(f"Response data: {ret.responseData}")
            return ret.responseData

    async def on_event(self, eventType, eventData):
        logging.debug(f"|{self._name}| New event! Type: {eventType}")
        logging.debug(f"Raw Data: {eventData}")

    async def on_scene_switched(self, eventData):
        """
        This method is called when a scene is switched.

        :param eventData:   A dictionary containing information about the scene
                            switch event
        :type eventData:    dict

        Data Fields:
        Name    Type    Description
        sceneName  String  Name of the scene that was switched to
        """
        logging.debug(
            f'|{self._name}| Scene switched to {eventData["sceneName"]}'
        )
        if self._name == "twitch" and eventData["sceneName"] == "Scene: Outro":
            await self.event_update_credits()
        await EventModule.queue_event(event="sync_scene", event_data=eventData)

    async def sync_scene_switch(self, event_data):
        if self._role == ModuleRole.FOLLOWER:
            await self.call_switch_scene(scene_name=event_data["sceneName"])

    async def on_stream_toggled(self, eventData):
        """
        Handle an event when stream is toggled.

        :param eventData: Dictionary containing data about the event
        :type eventData: dict

        Data Fields:
        - outputActive: Boolean, Whether the output is active
        - outputState: String, The specific state of the output
        """
        logging.debug(f"|{self._name}| Stream state changed:")
        logging.debug(eventData["outputActive"])
        logging.debug(eventData["outputState"])
        if (
            eventData["outputActive"] is True
            and self._role == ModuleRole.LEADER
        ):
            SessionData.start_session()

    async def on_record_toggled(self, eventData):
        """
        Handle an event when record is toggled.

        :param eventData: Dictionary containing data about the event
        :type eventData: dict

        Data Fields:
        - outputActive: Boolean, Whether the output is active
        - outputState:  String, The specific state of the output
        - outputPath:   String, File name for the saved recording,
                        if record stopped. null otherwise.
        """
        logging.debug(f"|{self._name}| Recording state changed:")
        logging.debug(eventData["outputActive"])
        logging.debug(eventData["outputState"])
        logging.debug(eventData["outputPath"])
        AsyncioThread.run_coroutine(
            EventModule.queue_event(
                event="sync_recording", record_status=eventData["outputActive"]
            )
        )

    async def sync_record_toggle(self, record_status):
        if self._role == ModuleRole.FOLLOWER:
            if record_status:
                request = simpleobsws.Request(
                    "StartRecord",
                )
            else:
                request = simpleobsws.Request(
                    "StopRecord",
                )
            await self.call(type="Toggle recording state", request=request)
        if self._role == ModuleRole.LEADER:
            SessionData.write_playlist_to_file()

    @check_obs_sources
    async def call_toggle_filter(
        self,
        source_name: str = None,
        filter_name: str = None,
        filter_enabled: bool = False,
    ):
        request = simpleobsws.Request(
            "SetSourceFilterEnabled",
            {
                "sourceName": f"{source_name}",
                "filterName": f"{filter_name}",
                "filterEnabled": filter_enabled,
            },
        )
        await self.call(type="Toggle filter", request=request)

    @check_obs_sources
    async def call_switch_scene(
        self,
        scene_name: str = None,
    ):
        request = simpleobsws.Request(
            "SetCurrentProgramScene",
            {
                "sceneName": f"{scene_name}",
            },
        )
        await self.call(type="Switch scene", request=request)

    @check_obs_sources
    async def call_update_text(self, input_name: str = None, text: str = None):
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"{input_name}",
                "inputSettings": {
                    "text": f"{text}",
                },
            },
        )
        await self.call(type="Update text", request=request)

    @check_obs_sources
    async def call_get_item_id(
        self, scene_name: str = None, source_name: str = None
    ):
        request = simpleobsws.Request(
            "GetSceneItemId",
            {"sceneName": f"{scene_name}", "sourceName": f"{source_name}"},
        )
        result = await self.call(type="Get SceneItem id", request=request)
        return result["sceneItemId"]

    @check_obs_sources
    async def call_update_position(
        self,
        scene_name: str = None,
        source_name: str = None,
        position_x: int = 0,
        position_y: int = 0,
    ):
        scene_item_id = await self.call_get_item_id(
            scene_name=scene_name, source_name=source_name
        )

        request = simpleobsws.Request(
            "SetSceneItemTransform",
            {
                "sceneName": f"{scene_name}",
                "sceneItemId": scene_item_id,
                "sceneItemTransform": {
                    "positionY": position_y,
                    "positionX": position_x,
                },
            },
        )
        await self.call(type="Update item position", request=request)

    @check_obs_sources
    async def call_update_url(self, input_name: str = None, url: str = None):
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"{input_name}",
                "inputSettings": {
                    "url": f"{url}",
                },
            },
        )
        await self.call(type="Update url", request=request)

    async def eventTriggerSlideAnimation(self):
        await self.call_toggle_filter("Track: Small", "Slide", True)
        await asyncio.sleep(9)

    async def eventUpdateTrackInfoThenTriggerBigSlideAnimation(self):
        await asyncio.gather(
            self.call_update_text(
                input_name="Big track artist",
                text=SessionData.current_artist(),
            ),
            self.call_update_text(
                input_name="Big track title",
                text=SessionData.current_title(),
            ),
        )
        await self.call_toggle_filter("Track: Big", "Slide", True)
        await asyncio.sleep(9)

    async def event_new_track(self):
        if self._name == "podcast":
            await self.eventTriggerSlideAnimationThenUpdateSmallTrackInfo()
        else:
            await self.eventUpdateSmallTrackInfoThenTriggerSlideAnimation()

    async def event_track_id(self):
        if self._name == "podcast":
            pass
        else:
            await self.eventUpdateTrackInfoThenTriggerBigSlideAnimation()

    async def event_shoutout(
        self,
        username: str = "Unknown",
        message: str = "Unknown",
        avatar_url: str = "https://loremflickr.com/300/300/twitch",
    ):
        if self._name == "podcast":
            pass
        else:
            await self.eventUpdateShoutoutTextThenTriggerSlideAnimation(
                username=username, message=message, avatar_url=avatar_url
            )

    async def eventUpdateSmallTrackInfoThenTriggerSlideAnimation(self):
        await asyncio.gather(
            self.call_update_text(
                input_name="Small track artist",
                text=SessionData.current_artist(),
            ),
            self.call_update_text(
                input_name="Small track title",
                text=SessionData.current_title(),
            ),
        )
        await self.call_toggle_filter("Track: Small", "Slide", True)
        await asyncio.sleep(9)

    async def eventTriggerSlideAnimationThenUpdateSmallTrackInfo(self):
        await self.call_toggle_filter("Track: Small", "Slide", True)
        await asyncio.sleep(1)
        await asyncio.gather(
            self.call_update_text(
                input_name="Small track artist",
                text=SessionData.current_artist(),
            ),
            self.call_update_text(
                input_name="Small track title",
                text=SessionData.current_title(),
            ),
        )
        await asyncio.sleep(6)

    async def eventUpdateShoutoutTextThenTriggerSlideAnimation(
        self,
        username: str = "Unknown",
        message: str = "Unknown",
        avatar_url: str = "https://loremflickr.com/300/300/twitch",
    ):
        await asyncio.gather(
            self.call_update_text(
                input_name="Shoutout username", text=username
            ),
            self.call_update_text(input_name="Shoutout message", text=message),
            self.call_update_url(input_name="Shoutout avatar", url=avatar_url),
        )
        await self.call_toggle_filter("Shoutout", "Slide", True)
        await asyncio.sleep(12)

    async def event_update_stats(self):
        if self._name == "twitch":
            asyncio.gather(
                self.call_update_text(
                    input_name="Stat: Messages",
                    text=SessionData.comments_count(),
                ),
                self.call_update_text(
                    input_name="Stat: Tracks",
                    text=SessionData.tracks_count(),
                ),
            )

    async def event_clear_credits(self):
        items = ["Setlist", "Followers", "Raids", "Moderators"]
        for item in items:
            await self.call_blank_text(input_name=item + ", header")
            await self.call_blank_text(input_name=item + ", list")

    async def event_update_credits(self):
        credits = SessionData.process_session_credits()
        for item in credits:
            await self.call_update_text_extended(item)

    async def event_moderator(self, moderator: str = None):
        if self._name == "video":
            await asyncio.gather(
                self.call_update_text(
                    input_name="Text, supertitle", text="MODERATOR"
                ),
                self.call_update_text(
                    input_name="Text, outline", text=moderator
                ),
                self.call_update_text(input_name="Text, fill", text=moderator),
                self.call_update_text(
                    input_name="Text, subtitle", text="IS IN THE HOUSE"
                ),
            )
            await self.call_toggle_filter(
                source_name="Animation",
                filter_name="Start animation",
                filter_enabled=True,
            )
            logging.debug("Animation started...")
            await asyncio.sleep(10)
            logging.debug("... animation completed")
            await self.reset_video_texts()

    async def event_vip(self, vip: str = None):
        if self._name == "video":
            await asyncio.gather(
                self.call_update_text(
                    input_name="Text, supertitle", text="VIP"
                ),
                self.call_update_text(input_name="Text, outline", text=vip),
                self.call_update_text(input_name="Text, fill", text=vip),
                self.call_update_text(
                    input_name="Text, subtitle", text="IN THE BUILDING"
                ),
            )
            await self.call_toggle_filter(
                source_name="Animation",
                filter_name="Start animation",
                filter_enabled=True,
            )
            logging.debug("Animation started...")
            await asyncio.sleep(10)
            logging.debug("... animation completed")
            await self.reset_video_texts()

    async def event_new_follower(self, username: str = None):
        if self._name == "video":
            await asyncio.gather(
                self.call_update_text(
                    input_name="Text, supertitle", text="NEW FOLLOWER"
                ),
                self.call_update_text(
                    input_name="Text, outline", text=username
                ),
                self.call_update_text(input_name="Text, fill", text=username),
            )
            await self.call_toggle_filter(
                source_name="Animation",
                filter_name="Start animation",
                filter_enabled=True,
            )
            logging.debug("Animation started...")
            await asyncio.sleep(10)
            logging.debug("... animation completed")
            await self.reset_video_texts()

    async def event_raid(self, name: str = None, count: int = None):
        if self._name == "video":
            raid_text = f"{name} x {count}"
            await asyncio.gather(
                self.call_update_text(
                    input_name="Text, supertitle", text="INCOMING RAID"
                ),
                self.call_update_text(
                    input_name="Text, outline", text=raid_text
                ),
                self.call_update_text(input_name="Text, fill", text=raid_text),
                self.call_update_text(
                    input_name="Text, subtitle", text="WELCOME EVERYONE"
                ),
            )
            await self.call_toggle_filter(
                source_name="Animation",
                filter_name="Start animation",
                filter_enabled=True,
            )
            logging.debug("Animation started...")
            await asyncio.sleep(10)
            logging.debug("... animation completed")
            await self.reset_video_texts()

    async def event_change_video(self, video: str = None):
        if self._name == "video":
            await self.call_update_input_source(
                input_name="Video", input_source=video
            ),

    async def call_update_text_extended(self, item: OBSText = None):
        await self.call_update_position(
            scene_name=item.scene,
            source_name=item.source,
            position_x=item.position_x,
            position_y=item.position_y,
        )
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": item.source,
                "inputSettings": {
                    "text": item.text,
                    "extents_cx": item.width,
                    "extents_cy": item.height,
                },
            },
        )
        await self.call(type="Update text extended", request=request)

    @check_obs_sources
    async def call_blank_text(self, input_name: str = None):
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": input_name,
                "inputSettings": {
                    "text": "",
                },
            },
        )
        await self.call(type=f"Blanking {input_name}", request=request)

    @check_obs_sources
    async def call_update_input_source(
        self, input_name: str = None, input_source: str = None
    ):
        video_path = (
            f"C:/Users/micro/Documents/OBS/video-sources/{input_source}"
        )
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"{input_name}",
                "inputType": "ffmpeg_source",
                "inputSettings": {
                    "local_file": f"{video_path}",
                },
            },
        )
        await self.call(
            type=f"Changing {input_name}: {input_source}", request=request
        )

    async def reset_video_texts(self):
        await asyncio.gather(
            self.call_blank_text(input_name="Text, supertitle"),
            self.call_blank_text(input_name="Text, outline"),
            self.call_blank_text(input_name="Text, fill"),
            self.call_blank_text(input_name="Text, subtitle"),
        )
