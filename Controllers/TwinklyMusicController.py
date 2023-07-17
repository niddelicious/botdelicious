import asyncio
import logging
import random
import string

import requests
from Helpers.Enums import TwinklyMusic


class TwinklyMusicController:
    def __init__(self, twinkly_music_url):
        self.unit_url = twinkly_music_url
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

    @_handshake
    async def run_twinkly_music(
        self, music: TwinklyMusic = TwinklyMusic.DANCE_SHUFFLE
    ):
        json_payload = {
            "auto_mood_mode": 1,
            "mood_index": music.value[0],
            "effect_index": music.value[1],
        }
        requests.post(
            self.unit_url + "music/config",
            json=json_payload,
            headers=self.headers,
        )
