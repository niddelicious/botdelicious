import asyncio
import logging
import random
import string

import requests
from Helpers.Enums import TwinklyEffect, TwinklyReact, TwinklyPlaylist


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
        json_payload = {"mode": "effect", "effect_id": effect_id}
        requests.post(
            self.unit_url + "led/mode", json=json_payload, headers=self.headers
        )

        if time is not None:
            await asyncio.sleep(time)
            await self.reset_lights()
        else:
            self.set_settings("effect", {"effect": effect})

    @_handshake
    async def run_twinkly_playlist(
        self,
        effect: TwinklyPlaylist = TwinklyPlaylist.RAINBOW_WAVES,
        time: int = 10,
    ):
        playlist_item = {"id": effect.value}
        effect = {"mode": "playlist"}
        requests.post(
            self.unit_url + "led/mode", json=effect, headers=self.headers
        )
        requests.post(
            self.unit_url + "playlist/current",
            json=playlist_item,
            headers=self.headers,
        )

        await asyncio.sleep(time)
        await self.reset_lights()

    @_handshake
    async def run_twinkly_react(
        self, react: TwinklyReact = TwinklyReact.BEAT_HUE
    ):
        react_id = react.value
        # json_payload = {
        #     "mode": "effect",
        #     "react_id": TwinklyReact.index(react),
        # }
        # requests.post(
        #     self.unit_url + "led/mode", json=json_payload, headers=self.headers
        # )

        react_mode = {"unique_id": react_id}
        json_payload = {"mode": "musicreactive"}

        logging.debug(f"React: {react.name}")
        requests.post(
            self.unit_url + "led/mode", json=json_payload, headers=self.headers
        )
        requests.post(
            self.unit_url + "music/drivers/current",
            json=react_mode,
            headers=self.headers,
        )
        self.set_settings("react", {"react": react})

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
