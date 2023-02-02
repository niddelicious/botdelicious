import asyncio
import logging
import simpleobsws

from helpers.AbstractModule import BotdeliciousModule
from helpers.Enums import ModuleStatus


class OBS(BotdeliciousModule):
    def __init__(
        self, port: str, password: str, name: str = "OBS", enableCallbacks: bool = False
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
            self.ws.register_event_callback(self.on_event)
            self.ws.register_event_callback(self.on_switchscenes, "SwitchScenes")

    async def disconnect(self):
        logging.info(f"Disconnecting from {self.name}")
        await self.ws.disconnect()

    async def on_event(eventType, eventData):
        logging.info(
            "New event! Type: {} | Raw Data: {}".format(eventType, eventData)
        )  # Print the event data. Note that `update-type` is also provided in the data

    async def on_switchscenes(eventData):
        logging.info('Scene switched to "{}".'.format(eventData["sceneName"]))

    async def changeSmallTrackInfoThenDisplayElement(
        self, artist: str = "Unknown", title: str = "Unknown"
    ):
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"Small track artist",
                "inputSettings": {
                    "text": f"{artist}",
                },
            },
        )
        ret = await self.ws.call(request)

        if ret.ok():  # Check if the request succeeded
            print("Request succeeded! Response data: {}".format(ret.responseData))

        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"Small track title",
                "inputSettings": {
                    "text": f"{title}",
                },
            },
        )
        ret = await self.ws.call(request)

        if ret.ok():  # Check if the request succeeded
            print("Request succeeded! Response data: {}".format(ret.responseData))

        request = simpleobsws.Request(
            "SetSourceFilterEnabled",
            {
                "sourceName": f"Track: Small",
                "filterName": "Slide",
                "filterEnabled": True,
            },
        )
        ret = await self.ws.call(request)  # Perform the request

        if ret.ok():  # Check if the request succeeded
            print("Request succeeded! Response data: {}".format(ret.responseData))

    async def displayElementThenChangeSmallTrackInfo(
        self, artist: str = "Unknown", title: str = "Unknown"
    ):

        request = simpleobsws.Request(
            "SetSourceFilterEnabled",
            {
                "sourceName": f"Track: Small",
                "filterName": "Slide",
                "filterEnabled": True,
            },
        )
        ret = await self.ws.call(request)  # Perform the request

        await asyncio.sleep(1)

        if ret.ok():  # Check if the request succeeded
            print("Request succeeded! Response data: {}".format(ret.responseData))
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"Small track artist",
                "inputSettings": {
                    "text": f"{artist}",
                },
            },
        )
        ret = await self.ws.call(request)

        if ret.ok():  # Check if the request succeeded
            print("Request succeeded! Response data: {}".format(ret.responseData))

        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"Small track title",
                "inputSettings": {
                    "text": f"{title}",
                },
            },
        )
        ret = await self.ws.call(request)

        if ret.ok():  # Check if the request succeeded
            print("Request succeeded! Response data: {}".format(ret.responseData))
