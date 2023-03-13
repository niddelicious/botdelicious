import asyncio
import logging
import simpleobsws

from helpers.AbstractModule import BotdeliciousModule
from helpers.ConfigManager import ConfigManager
from helpers.Enums import ModuleStatus
from helpers.SessionData import SessionData


class OBSModule(BotdeliciousModule):
    _running_instances = []

    def __init__(self, name: str = "obs") -> None:
        super().__init__()
        self._name = name
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
        self.enableCallbacks = self.config.callbacks
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
        if self.enableCallbacks:
            # self.ws.register_event_callback(self.on_event)
            # self.ws.register_event_callback(self.on_switchscenes, "SwitchScenes")
            pass

    async def disconnect(self):
        logging.info(f"Disconnecting from {self._name}")
        await self.ws.disconnect()

    async def on_event(eventType, eventData):
        logging.info(
            "New event! Type: {} | Raw Data: {}".format(eventType, eventData)
        )  # Print the event data. Note that `update-type` is also provided in the data

    async def on_switchscenes(eventData):
        logging.info('Scene switched to "{}".'.format(eventData["sceneName"]))

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
                text=SessionData.get_current_artist(),
            ),
            self.callUpdateText(
                inputName="Big track title",
                text=SessionData.get_current_title(),
            ),
        )
        await self.callToggleFilter("Track: Big", "Slide", True)
        await asyncio.sleep(9)

    async def eventUpdateSmallTrackInfoThenTriggerSlideAnimation(self):
        await asyncio.gather(
            self.callUpdateText(
                inputName="Small track artist",
                text=SessionData.get_current_artist(),
            ),
            self.callUpdateText(
                inputName="Small track title",
                text=SessionData.get_current_title(),
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
                text=SessionData.get_current_artist(),
            ),
            self.callUpdateText(
                inputName="Small track title",
                text=SessionData.get_current_title(),
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
