import re
import requests


class Utilities:
    @classmethod
    def find_username(cls, message):
        twitch_username_pattern = "@(\w+)"
        res = re.search(twitch_username_pattern, message)
        if not res:
            res = message.split(" ")
            if len(res) > 1:
                return res[1]
            else:
                return False
        return res.group(1)

    @classmethod
    async def get_user_info(
        cls,
        username: str = None,
        client_id: str = None,
        access_token: str = None,
    ):
        url = "https://api.twitch.tv/helix/users"
        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}",
        }
        params = {"login": username}
        response = requests.get(url, headers=headers, params=params)
        if len(response.json()["data"]) == 0:
            return None
        return response.json()["data"][0]

    @classmethod
    async def get_channel_info(
        cls,
        user_id: str = None,
        client_id: str = None,
        access_token: str = None,
    ):
        url = f"https://api.twitch.tv/helix/channels?broadcaster_id={user_id}"
        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.get(url, headers=headers)
        return response.json()["data"][0]

    @classmethod
    async def get_live_stream_info(
        cls,
        user_id: str = None,
        client_id: str = None,
        access_token: str = None,
    ):
        url = "https://api.twitch.tv/helix/streams"
        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}",
        }
        params = {"user_id": user_id, "type": "live"}
        response = requests.get(url, headers=headers, params=params)
        if len(response.json()["data"]) == 0:
            return None
        return response.json()["data"][0]
