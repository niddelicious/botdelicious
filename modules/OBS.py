import asyncio
import logging
import simpleobsws

from helpers.AbstractModule import BotdeliciousModule
from helpers.ConfigManager import ConfigManager
from helpers.Enums import ModuleStatus


class OBSModule(BotdeliciousModule):
    def __init__(self, name: str = "obs") -> None:
        super().__init__()
        self._name = name
        self.config = None
        self._status = ModuleStatus.IDLE

    async def start(self):
        self._status = ModuleStatus.RUNNING
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

    def _status(self):
        return self._status

    async def stop(self):
        self._status = ModuleStatus.STOPPING
        await self.disconnect()
        self._status = ModuleStatus.IDLE

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

    async def eventTriggerBigSlideAnimation(self):
        await self.callToggleFilter("Track: Big", "Slide", True)
        await asyncio.sleep(9)

    async def eventUpdateSmallTrackInfoThenTriggerSlideAnimation(
        self, artist: str = "Unknown", title: str = "Unknown"
    ):
        await asyncio.gather(
            self.callUpdateText(inputName="Small track artist", text=artist),
            self.callUpdateText(inputName="Small track title", text=title),
        )
        await self.callToggleFilter("Track: Small", "Slide", True)
        await asyncio.sleep(9)

    async def eventTriggerSlideAnimationThenUpdateSmallTrackInfo(
        self, artist: str = "Unknown", title: str = "Unknown"
    ):
        await self.callToggleFilter("Track: Small", "Slide", True)
        await asyncio.sleep(1)
        await asyncio.gather(
            self.callUpdateText(inputName="Small track artist", text=artist),
            self.callUpdateText(inputName="Small track title", text=title),
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
