import asyncio
import logging


class EventLoopManager:
    def __init__(self, queue=None):
        self.queue = queue
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def start(self):
        self.loop.run_forever()

    def checkLoopIsRunning(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logging.error(f"No running event loop!")
        else:
            logging.debug(f"Running event loop found: {loop}")
        self.queue.put("EventLoopManager Done!")
