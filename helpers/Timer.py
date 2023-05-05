import asyncio
from typing import Callable, Dict, List
import time


class Timer:
    _timers: Dict[str, asyncio.Task] = {}
    _timer_start_times: Dict[str, float] = {}

    @classmethod
    async def _timer_task(cls, name: str, duration: float, callback: Callable):
        cls._timer_start_times[name] = time.time()
        await asyncio.sleep(duration)
        callback()
        del cls._timers[name]
        del cls._timer_start_times[name]

    @classmethod
    async def start(
        cls,
        name: str,
        duration: float,
        callback: Callable,
        denied_callback: Callable = None,
    ):
        if name in cls._timers:
            if denied_callback:
                denied_callback()
            return

        task = asyncio.create_task(cls._timer_task(name, duration, callback))
        cls._timers[name] = task

    @classmethod
    def is_running(cls, name: str) -> bool:
        return name in cls._timers

    @classmethod
    def get_running_timers(cls) -> Dict[str, asyncio.Task]:
        return cls._timers

    @classmethod
    def time_left(cls, name: str) -> str:
        if name not in cls._timer_start_times:
            raise ValueError(f"No timer with the name '{name}' is running.")

        elapsed_time = time.time() - cls._timer_start_times[name]
        remaining_time = (
            cls._timers[name]._coro.cr_frame.f_locals["duration"]
            - elapsed_time
        )

        hours, remainder = divmod(remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        time_str = ""
        if hours:
            time_str += f"{int(hours)}h "
        if minutes:
            time_str += f"{int(minutes)}m "
        time_str += f"{int(seconds)}s"

        return time_str

    @classmethod
    def timers(cls) -> List[Dict[str, str]]:
        running_timers = []
        for name in cls._timers:
            running_timers.append(
                {"name": name, "time_left": cls.time_left(name)}
            )

        return running_timers
