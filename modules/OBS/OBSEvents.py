import asyncio
import logging
import simpleobsws
from Enums import ModuleRole
from abc import ABC, abstractmethod
from SessionData import SessionData

from Modules.EventModule import EventModule


class OBSEvents(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def scene_switched(self, eventData):
        pass

    @abstractmethod
    async def stream_toggled(self, eventData):
        pass

    @abstractmethod
    async def record_toggled(self, eventData):
        pass

    @abstractmethod
    async def small_track(self):
        pass

    @abstractmethod
    async def big_track(self):
        pass

    @abstractmethod
    async def fire(self):
        pass

    @abstractmethod
    async def tune(self):
        pass

    @abstractmethod
    async def new_track(self):
        pass

    @abstractmethod
    async def track_id(self):
        pass

    @abstractmethod
    async def shoutout(
        self,
        username: str = "Unknown",
        message: str = "Unknown",
        avatar_url: str = "https://loremflickr.com/300/300/twitch",
    ):
        pass

    @abstractmethod
    async def update_stats(self):
        pass

    @abstractmethod
    async def clear_credits(self):
        pass

    @abstractmethod
    async def update_credits(self):
        pass

    @abstractmethod
    async def moderator_active(self, moderator: str = None):
        pass

    @abstractmethod
    async def vip_active(self, vip: str = None):
        pass

    @abstractmethod
    async def chatter_active(self, chatter: str = None):
        pass

    @abstractmethod
    async def new_follower(self, username: str = None, avatar_url: str = None):
        pass

    @abstractmethod
    async def raid(
        self, raider: str = None, count: int = None, avatar_url: str = None
    ):
        pass

    @abstractmethod
    async def change_background_video(self, video: str = None):
        pass
