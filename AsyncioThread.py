import asyncio
import threading


class AsyncioThread:
    _loop = None
    _thread = None

    @classmethod
    def get_event_loop(cls):
        return cls._loop

    @classmethod
    def start_loop(cls):
        cls._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls._loop)
        cls._thread = threading.Thread(target=cls._loop.run_forever)
        cls._thread.start()

    @classmethod
    def stop_loop(cls):
        if cls._loop is not None:
            cls._loop.call_soon_threadsafe(cls._loop.stop)
            cls._thread.join()
            cls._loop = None
            cls._thread = None

    @classmethod
    def run_coroutine(cls, coro):
        if cls._loop is None:
            cls.start_loop()
        asyncio.run_coroutine_threadsafe(coro, cls._loop)
