import asyncio
import logging
import simpleobsws

from helpers.AbstractModule import BotdeliciousModule
from helpers.Enums import ModuleStatus


class OBS(BotdeliciousModule):
    def __init__(
        self,
        port: str,
        password: str,
        name: str = "OBS",
        enableCallbacks: bool = False,
    ) -> None:
        super().__init__()
        parameters = (
            simpleobsws.IdentificationParameters()
        )  # Create an IdentificationParameters object
        parameters.eventSubscriptions = (1 << 0) | (
            1 << 2
        )  # Subscribe to the General and Scenes categories
        self.ws = simpleobsws.WebSocketClient(
            url=f"ws://127.0.0.1:{port}",
            password=password,
            identification_parameters=parameters,
        )
        self.name = name
        self.enableCallbacks = enableCallbacks

    def start(self):
        self.status = ModuleStatus.RUNNING
        pass

    def status(self):
        return self.status

    def stop(self):
        pass

    async def connect(self, *args, **kwargs):
        logging.info(f"Connecting to {self.name}...")
        try:
            await self.ws.connect()
            await self.ws.wait_until_identified()
        except ConnectionError:
            logging.warn(f"Could not connect to {self.name}")
            return
        if self.enableCallbacks:
            # self.ws.register_event_callback(self.on_event)
            # self.ws.register_event_callback(self.on_switchscenes, "SwitchScenes")
            pass

    async def disconnect(self):
        logging.info(f"Disconnecting from {self.name}")
        await self.ws.disconnect()

    async def on_event(eventType, eventData):
        logging.info(
            "New event! Type: {} | Raw Data: {}".format(eventType, eventData)
        )  # Print the event data. Note that `update-type` is also provided in the data

    async def on_switchscenes(eventData):
        logging.info('Scene switched to "{}".'.format(eventData["sceneName"]))

    async def eventUpdateSmallTrackInfoThenTriggerSlideAnimation(
        self, artist: str = "Unknown", title: str = "Unknown"
    ):
        await asyncio.gather(
            self.callUpdateText(inputName="Small track artist", text=artist),
            self.callUpdateText(inputName="Small track title", text=title),
        )
        await self.callToggleFilter("Track: Small", "Slide", True)
        await asyncio.sleep(8)

    async def eventTriggerSlideAnimationThenUpdateSmallTrackInfo(
        self, artist: str = "Unknown", title: str = "Unknown"
    ):
        await self.callToggleFilter("Track: Small", "Slide", True)
        await asyncio.sleep(1)
        await asyncio.gather(
            self.callUpdateText(inputName="Small track artist", text=artist),
            self.callUpdateText(inputName="Small track title", text=title),
        )
        await asyncio.sleep(5)

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
                "Filter toggle succeeded! Response data: {}".format(ret.responseData)
            )
            return True
        else:
            logging.warn(
                "Filter toggle failed! Response data: {}".format(ret.responseData)
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
                "Input update succeeded! Response data: {}".format(ret.responseData)
            )
            return True
        else:
            logging.warn(
                "Input update failed! Response data: {}".format(ret.responseData)
            )
            return False
