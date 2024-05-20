import httpx
import logging
from dotmap import DotMap
from Controllers.ConfigController import ConfigController


class TwitchUpdateTool:

    def __init__(self):
        self.config = ConfigController.get_config_file("twitch_channel.yaml")
        self.config_file = "twitch_channel.yaml"
        self.broadcaster_id = self.config.auth.broadcaster_id
        self.client_id = self.config.auth.channel_update_client_id
        self.client_secret = self.config.auth.channel_update_client_secret
        self.access_token = self.config.auth.channel_update_access_token
        self.refresh_token = self.config.auth.channel_update_refresh_token
        self.url = "https://api.twitch.tv/helix/channels"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Client-Id": f"{self.client_id}",
            "Content-Type": "application/json",
        }

    def update_twitch_channel(self, title=None, category_id=None, tags=None):

        payload = {
            "broadcaster_id": self.broadcaster_id,
            "title": title,
            "game_id": category_id,
            "tags": tags,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        try:
            response = httpx.patch(self.url, headers=self.headers, json=payload)
            if response.status_code == 204:
                return True
            else:
                raise Exception(response.text)
        except Exception as e:
            logging.error(f"Failed to update Twitch channel: {e}")
            return False

    def title_assembler(self, series, episode, genre, tagline):
        title = f"{genre} | {series} #{episode} | {tagline}"
        return title

    def genre_to_tags(self, genre, tags=None):
        genre = genre.replace(" ", "")
        if "-" in genre:
            genres = genre.split("-")
        else:
            genres = [genre]
        for g in genres:
            if len(g) > 20:
                g = g[:20]
            if g not in tags:
                tags.append(g)
        return tags

    def refresh_tokens(self):
        logging.debug("Refreshing Channel Updater tokens")
        twitch_refresh_url = str(
            f"https://id.twitch.tv/oauth2/token?"
            f"grant_type=refresh_token&"
            f"refresh_token={self.refresh_token}&"
            f"client_id={self.client_id}&"
            f"client_secret={self.config.client_secret}"
        )
        refresh = DotMap(httpx.post(twitch_refresh_url).json())
        logging.debug(f"Refresh response: {refresh}")
        if self.config.access_token != refresh.access_token:
            ConfigController.update_config_file(
                self.config_file,
                "auth",
                "channel_update_access_token",
                refresh.channel_update_access_token,
            )

        if self.config.refresh_token != refresh.refresh_token:
            ConfigController.update_config_file(
                self.config_file,
                "auth",
                "channel_update_refresh_token",
                refresh.refresh_token,
            )

        logging.info("Refreshed Twitch Chat Tokens")
        return True
