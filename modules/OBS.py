import asyncio
import logging
import simpleobsws


class OBS:
    def __init__(self, port, password, name="OBS", enableCallbacks=False) -> None:
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

    async def connect(self, *args, **kwargs):
        logging.info(f"-- Connecting to {self.name}...")
        try:
            await self.ws.connect()
            await self.ws.wait_until_identified()
            logging.info(f"-- ... connected")
        except ConnectionError:
            logging.warn(f".... couldn't find {self.name}")
            return
        if self.enableCallbacks:
            self.ws.register_event_callback(self.on_event)
            self.ws.register_event_callback(self.on_switchscenes, "SwitchScenes")

    async def on_event(eventType, eventData):
        logging.info(
            "New event! Type: {} | Raw Data: {}".format(eventType, eventData)
        )  # Print the event data. Note that `update-type` is also provided in the data

    async def on_switchscenes(eventData):
        logging.info('Scene switched to "{}".'.format(eventData["sceneName"]))