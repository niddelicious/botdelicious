import asyncio
import logging
import simpleobsws

from helpers.AbstractModule import BotdeliciousModule
from helpers.ConfigManager import ConfigManager
from helpers.Enums import ModuleStatus
from helpers.Enums import ModuleRole
from helpers.SessionData import SessionData


class OBSModule(BotdeliciousModule):
    _running_instances = []

    def __init__(self, name: str = "obs") -> None:
        super().__init__()
        self._name = name
        self._role = ModuleRole.FOLLOWER
        self.config = None

    async def start(self):
        self.set_status(ModuleStatus.RUNNING)
        self.config = getattr(ConfigManager._config, self._name)
        parameters = simpleobsws.IdentificationParameters()
        parameters.eventSubscriptions = (1 << 0) | (1 << 2)
        self.ws = simpleobsws.WebSocketClient(
            url=f"ws://127.0.0.1:{self.config.port}",
            password=self.config.password,
            identification_parameters=parameters,
        )
        self._role = (
            ModuleRole.LEADER if self.config.callbacks else ModuleRole.FOLLOWER
        )
        await self.connect()
        self.add_running_instance(self._name)

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        await self.disconnect()
        self.remove_running_instance(self._name)
        self.set_status(ModuleStatus.IDLE)

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
            # self.ws.register_event_callback(self.on_event)
            # self.ws.register_event_callback(self.on_scene_switched, "CurrentProgramSceneChanged")
            # self.ws.register_event_callback(self.on_record_toggled, "RecordStateChanged")
            pass

    async def disconnect(self):
        logging.info(f"Disconnecting from {self._name}")
        await self.ws.disconnect()

    async def on_event(eventType, eventData):
        logging.info(
            "New event! Type: {} | Raw Data: {}".format(eventType, eventData)
        )  # Print the event data. Note that `update-type` is also provided in the data

    async def on_scene_switched(eventData):
        """
        This method is called when a scene is switched.

        :param eventData: A dictionary containing information about the scene switch event
        :type eventData: dict

        Data Fields:
        Name    Type    Description
        sceneName  String  Name of the scene that was switched to
        """
        logging.debug('Scene switched to "{}".'.format(eventData["sceneName"]))

    async def on_record_toggled(eventData):
        """
        Handle an event when record is toggled.

        :param eventData: Dictionary containing data about the event
        :type eventData: dict

        Data Fields:
        - outputActive: Boolean, Whether the output is active
        - outputState: String, The specific state of the output
        - outputPath: String, File name for the saved recording, if record stopped. null otherwise.
        """
        logging.debug("Recording state changed:")
        logging.debug(eventData["outputActive"])
        logging.debug(eventData["outputState"])
        logging.debug(eventData["outputPath"])

    async def callToggleFilter(
        self,
        sourceName: str = None,
        filterName: str = None,
        filterEnabled: bool = False,
    ):
        request = simpleobsws.Request(
            "SetSourceFilterEnabled",
            {
                "sourceName": f"{sourceName}",
                "filterName": f"{filterName}",
                "filterEnabled": filterEnabled,
            },
        )
        ret = await self.ws.call(request)  # Perform the request

        if ret.ok():  # Check if the request succeeded
            logging.debug(
                "Filter toggle succeeded! Response data: {}".format(
                    ret.responseData
                )
            )
            return True
        else:
            logging.warn(
                "Filter toggle failed! Response data: {}".format(
                    ret.responseData
                )
            )
            return False

    async def callUpdateText(self, inputName: str = None, text: str = None):
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"{inputName}",
                "inputSettings": {
                    "text": f"{text}",
                },
            },
        )
        ret = await self.ws.call(request)  # Perform the request

        if ret.ok():  # Check if the request succeeded
            logging.debug(
                "Input update succeeded! Response data: {}".format(
                    ret.responseData
                )
            )
            return True
        else:
            logging.warn(
                "Input update failed! Response data: {}".format(
                    ret.responseData
                )
            )
            return False

    async def callUpdateUrl(self, inputName: str = None, url: str = None):
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"{inputName}",
                "inputSettings": {
                    "url": f"{url}",
                },
            },
        )
        ret = await self.ws.call(request)  # Perform the request

        if ret.ok():  # Check if the request succeeded
            logging.info(
                "Input update succeeded! Response data: {}".format(
                    ret.responseData
                )
            )
            return True
        else:
            logging.warn(
                "Input update failed! Response data: {}".format(
                    ret.responseData
                )
            )
            return False

    async def eventTriggerSlideAnimation(self):
        await self.callToggleFilter("Track: Small", "Slide", True)
        await asyncio.sleep(9)

    async def eventUpdateTrackInfoThenTriggerBigSlideAnimation(self):
        await asyncio.gather(
            self.callUpdateText(
                inputName="Big track artist",
                text=SessionData.get_current_track().artist,
            ),
            self.callUpdateText(
                inputName="Big track title",
                text=SessionData.get_current_track().title,
            ),
        )
        await self.callToggleFilter("Track: Big", "Slide", True)
        await asyncio.sleep(9)

    async def eventUpdateSmallTrackInfoThenTriggerSlideAnimation(self):
        await asyncio.gather(
            self.callUpdateText(
                inputName="Small track artist",
                text=SessionData.get_current_track().artist,
            ),
            self.callUpdateText(
                inputName="Small track title",
                text=SessionData.get_current_track().title,
            ),
        )
        await self.callToggleFilter("Track: Small", "Slide", True)
        await asyncio.sleep(9)

    async def eventTriggerSlideAnimationThenUpdateSmallTrackInfo(self):
        await self.callToggleFilter("Track: Small", "Slide", True)
        await asyncio.sleep(1)
        await asyncio.gather(
            self.callUpdateText(
                inputName="Small track artist",
                text=SessionData.get_current_track().artist,
            ),
            self.callUpdateText(
                inputName="Small track title",
                text=SessionData.get_current_track().title,
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
            self.callUpdateText(inputName="Shoutout username", text=username),
            self.callUpdateText(inputName="Shoutout message", text=message),
            self.callUpdateUrl(inputName="Shoutout avatar", url=avatar_url),
        )
        await self.callToggleFilter("Shoutout", "Slide", True)
        await asyncio.sleep(12)
