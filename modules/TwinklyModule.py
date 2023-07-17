import asyncio
import logging

from Modules.BotdeliciousModule import BotdeliciousModule
from Helpers.Enums import (
    ModuleStatus,
    TwinklyEffect,
    TwinklyMusic,
    TwinklyPlaylist,
)
from Controllers.ConfigController import ConfigController
from Controllers.TwinklyController import TwinklyController
from Controllers.TwinklyMusicController import TwinklyMusicController


class TwinklyModule(BotdeliciousModule):
    _lights = []
    _music: TwinklyMusicController

    def __init__(self):
        super().__init__()

    async def start(self, **kwargs):
        self.set_status(ModuleStatus.RUNNING)
        logging.debug(f"Starting lights")
        for light in ConfigController.get("twinkly"):
            self.add_light_instance(TwinklyController(light))
        for light in self.get_lights():
            await light.run_twinkly_color(red=255, green=178, blue=105)
        self._music = self.add_music(
            TwinklyMusicController(ConfigController.get("twinkly_music"))
        )

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        self.set_status(ModuleStatus.IDLE)

    @classmethod
    def get_lights(cls):
        return cls._lights

    @classmethod
    def add_light_instance(cls, instance):
        cls._lights.append(instance)

    @classmethod
    def get_music(cls):
        return cls._music

    @classmethod
    def add_music(cls, instance: TwinklyMusicController):
        cls._music = instance

    @classmethod
    async def effect(
        cls,
        effect: TwinklyEffect = TwinklyEffect.RAINBOW,
        time: int = None,
        *args,
        **kwargs,
    ):
        await asyncio.gather(
            *[
                light.run_twinkly_effect(effect, time)
                for light in cls.get_lights()
            ],
        )

    @classmethod
    async def playlist(
        cls,
        effect: TwinklyPlaylist = TwinklyPlaylist.RAINBOW_WAVES,
        time: int = 10,
        *args,
        **kwargs,
    ):
        await asyncio.gather(
            *[
                light.run_twinkly_playlist(effect, time)
                for light in cls.get_lights()
            ],
        )

    @classmethod
    async def music(
        cls, music: TwinklyMusic = TwinklyMusic.DANCE_SHUFFLE, *args, **kwargs
    ):
        await cls._music.run_twinkly_music(music)
        await asyncio.gather(
            *[light.run_twinkly_react(music) for light in cls.get_lights()],
        )

    @classmethod
    async def color(
        cls, red: int = 255, green: int = 255, blue: int = 255, *args, **kwargs
    ):
        await asyncio.gather(
            *[
                light.run_twinkly_color(red, green, blue)
                for light in cls.get_lights()
            ],
        )
