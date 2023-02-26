import asyncio
import threading
import queue


class AsyncioThread:
    _loop = None
    _thread = None

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


class MyClass:
    def __init__(self):
        self._asyncio_thread = None
        self._input_thread = None
        self._input_queue = queue.Queue()

    def start_asyncio_thread(self):
        self._asyncio_thread = AsyncioThread()
        self._asyncio_thread.start_loop()

    def stop_asyncio_thread(self):
        if self._asyncio_thread is not None:
            self._asyncio_thread.stop_loop()
            self._asyncio_thread = None

    def run_asyncio_coroutine(self, coro):
        if self._asyncio_thread is None:
            self.start_asyncio_thread()
        self._asyncio_thread.run_coroutine(coro)

    def start_input_thread(self):
        self._input_thread = threading.Thread(target=self._input_loop)
        self._input_thread.start()

    def stop_input_thread(self):
        self._input_queue.put('stop')
        self._input_thread.join()
        self._input_thread = None

    def _input_loop(self):
        while True:
            user_input = input()
            self._input_queue.put(user_input)
            if user_input == 'stop':
                break

    def wait_for_input(self):
        while True:
            user_input = self._input_queue.get()
            if user_input == 'stop':
                break


async def my_coroutine():
    while True:
        print("running my_coroutine")
        await asyncio.sleep(2)


my_object = MyClass()

# start the event loop
my_object.start_asyncio_thread()

# schedule a coroutine to run in the event loop
my_object.run_asyncio_coroutine(my_coroutine())

# start the input thread to listen for user input
my_object.start_input_thread()

# wait for the user to enter "stop"
my_object.wait_for_input()

# stop the input thread and the event loop
my_object.stop_input_thread()
my_object.stop_asyncio_thread()
