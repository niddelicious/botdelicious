import asyncio

class EventLoopManager:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def start(self):
        self.loop.run_forever()