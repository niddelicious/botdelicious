import random
import string
import requests

from helpers.AbstractModule import BotdeliciousModule
from helpers.Enums import ModuleStatus
from helpers.ConfigManager import ConfigManager


class TwinklyController:
    def __init__(self, twinkly_light_url):
        self.unit_url = twinkly_light_url
        self.headers = {}

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

    @_handshake
    async def run_twinkly_effect(self):
        effect = {"mode": "effect", "effect_id": 0}
        requests.post(
            self.unit_url + "led/mode", json=effect, headers=self.headers
        )


class TwinklyModule(BotdeliciousModule):
    _status = ModuleStatus.IDLE

    def __init__(self):
        self.default_mode = "movie"
        self.music_effect = "00000000-0000-0000-0000-000000000003"
        self.headers = {}
        self.lights = []

    async def start(self, **kwargs):
        self.set_status(ModuleStatus.RUNNING)
        for light in ConfigManager.get("twinkly"):
            self.lights.append(TwinklyController(light))
        for light in self.lights:
            await light.run_twinkly_effect()

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        self.set_status(ModuleStatus.IDLE)

    async def status(self):
        return self._status
