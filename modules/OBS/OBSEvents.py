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

    async def scene_switched(self, eventData):
        pass

    async def stream_toggled(self, eventData):
        pass

    async def record_toggled(self, eventData):
        pass

    async def small_track(self):
        pass

    async def big_track(self):
        pass

    async def fire(self):
        pass

    async def tune(self):
        pass

    async def new_track(self):
        pass

    async def track_id(self):
        pass


    async def shoutout(
        self,
        username: str = "Unknown",
        message: str = "Unknown",
        avatar_url: str = "https://loremflickr.com/300/300/twitch",
    ):
        pass


    async def update_stats(self):
        pass


    async def clear_credits(self):
        pass


    async def update_credits(self):
        pass


    async def moderator_active(self, moderator: str = None):
        pass


    async def vip_active(self, vip: str = None):
        pass


    async def chatter_active(self, chatter: str = None):
        pass


    async def new_follower(self, username: str = None, avatar_url: str = None):
        pass


    async def raid(
        self, raider: str = None, count: int = None, avatar_url: str = None
    ):
        pass


    async def change_background_video(self, video: str = None):
        pass
