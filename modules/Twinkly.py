import asyncio
import logging
import random
import string
import requests

from helpers.AbstractModule import BotdeliciousModule
from helpers.Enums import ModuleStatus, TwinklyEffect
from helpers.ConfigManager import ConfigManager


class TwinklyController:
    def __init__(self, twinkly_light_url):
        self.unit_url = twinkly_light_url
        self.headers = {}
        self._settings = {}

    def _handshake(func):
        async def wrapper(self, *args, **kwargs):
            await self._login_to_twinkly_unit()
            result = await func(self, *args, **kwargs)
            await self._logout_of_twinkly_unit()
            return result

        return wrapper

    async def _login_to_twinkly_unit(self, **kwargs):
        challenge_length = 32
        challenge = "".join(
            random.choices(
                string.ascii_uppercase + string.digits, k=challenge_length
            )
        )

        login_request = requests.post(
            self.unit_url + "login", json={"challenge": challenge}
        )
        login_response = login_request.json()

        self.headers = {"X-Auth-Token": login_response["authentication_token"]}

        requests.post(
            self.unit_url + "verify",
            json=login_response["challenge-response"],
            headers=self.headers,
        )

    async def _logout_of_twinkly_unit(self, **kwargs):
        requests.post(self.unit_url + "logout", headers=self.headers)

    def get_settings(self):
        return self._settings

    def set_settings(self, mode, options):
        self._settings = {
            "mode": mode,
            "options": options,
        }

    async def reset_lights(self):
        reset = self.get_settings()
        await getattr(self, f"run_twinkly_{reset['mode']}")(**reset["options"])

    @_handshake
    async def run_twinkly_effect(
        self, effect: TwinklyEffect = TwinklyEffect.RAINBOW, time: int = None
    ):
        effect_id = effect.value
        logging.debug(f"Effect: {effect_id}")
        effect = {"mode": "effect", "effect_id": effect_id}
        requests.post(
            self.unit_url + "led/mode", json=effect, headers=self.headers
        )

        if time is not None:
            await asyncio.sleep(time)
            await self.reset_lights()
        else:
            self.set_settings("effect", effect_id)

    @_handshake
    async def run_twinkly_react(self, react_id: int = 0):
        effect = {"mode": "effect", "react_id": react_id}
        requests.post(
            self.unit_url + "led/mode", json=effect, headers=self.headers
        )

        react_modes_list = [
            "00000000-0000-0000-0000-000000000001",  # VU Meter
            "00000000-0000-0000-0000-000000000002",  # Beat Hue | Shift color on beat
            "00000000-0000-0000-0000-000000000003",  # Psychedelica | Puslating color on beat
            "00000000-0000-0000-0000-000000000004",  # Red Vertigo | Heartbeat
            "00000000-0000-0000-0000-000000000005",  # Dancing Bands | Bands
            "00000000-0000-0000-0000-000000000006",  # Diamond Swirl | Diamond patterns
            "00000000-0000-0000-0000-000000000007",  # Joyful Stripes | Pusling bands
            "00000000-0000-0000-0000-000000000008",  # Elevator | Rising/falling bands
            "00000000-0000-0000-0000-000000000009",  # Angel Fade | Pulsing angles
            "00000000-0000-0000-0000-00000000000A",  # Clockwork | Spinning stripe
            "00000000-0000-0000-0000-00000000000B",  # Sipario | Wipes
            "00000000-0000-0000-0000-00000000000C",  # Sunset | Sunset with pulsing center
        ]

        if react_id < len(react_modes_list):
            react_code = react_modes_list[react_id]
        else:
            react_id = random.choice(range(len(react_modes_list)))
            react_code = react_modes_list[react_id]
        react_mode = {"unique_id": react_code}
        effect = {"mode": "musicreactive"}

        logging.debug(f"React: {react_id}")
        requests.post(
            self.unit_url + "led/mode", json=effect, headers=self.headers
        )
        requests.post(
            self.unit_url + "music/drivers/current",
            json=react_mode,
            headers=self.headers,
        )
        self.set_settings("react", react_id)

    @_handshake
    async def run_twinkly_color(
        self, red: int = 255, green: int = 255, blue: int = 255
    ):
        if not 0 <= red <= 255:
            red = 255
        if not 0 <= green <= 255:
            green = 255
        if not 0 <= blue <= 255:
            blue = 255

        rgb_values = {"red": red, "green": green, "blue": blue}

        logging.debug(f"Color: r{red} g{green} b{blue}")

        requests.post(
            self.unit_url + "led/color", json=rgb_values, headers=self.headers
        )
        effect = {"mode": "color"}
        requests.post(
            self.unit_url + "led/mode", json=effect, headers=self.headers
        )
        self.set_settings("color", rgb_values)


class TwinklyModule(BotdeliciousModule):
    _lights = []

    def __init__(self):
        super().__init__()

    async def start(self, **kwargs):
        self.set_status(ModuleStatus.RUNNING)
        logging.debug(f"Starting lights")
        for light in ConfigManager.get("twinkly"):
            self.add_light_instance(TwinklyController(light))
        for light in self.get_lights():
            await light.run_twinkly_color(red=255, green=178, blue=105)

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
    async def effect(cls, effect: TwinklyEffect = TwinklyEffect.RAINBOW, time: int = None, *args, **kwargs):
        await asyncio.gather(
            *[
                light.run_twinkly_effect(effect, time)
                for light in cls.get_lights()
            ],
        )

    @classmethod
    async def react(cls, react_id: int = 0, *args, **kwargs):
        await asyncio.gather(
            *[light.run_twinkly_react(react_id) for light in cls.get_lights()],
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
