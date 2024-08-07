import httpx
import logging
import re
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
        self.headers = {}
        self.update_headers()

    def update_headers(self):
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

    def title_override(self, title):
        print(f"Current title: {title}")
        new_title = input("Enter new title (press Enter to skip): ").strip()
        if new_title:
            title = f"{new_title} | {self.config.info.series} #{self.config.info.episode} | {self.config.info.tagline}"
        print(f"New title: {title}")
        overwrite_title = input(
            "Enter full new title or press Enter to accept: "
        ).strip()
        if overwrite_title:
            title = f"{overwrite_title}"
        return title

    def genre_to_tags(self, genre, tags=None):
        delimiters = r"[-,\.&|/\\;:\s]"
        genres = re.split(delimiters, genre)
        genres = [g for g in genres if g]
        for g in genres:
            if len(g) > 20:
                g = g[:20]
            if g not in tags and g.isalnum():
                tags.append(g)
        return tags

    def add_tags(self, tags=[]):
        print("Current tags: ", tags)
        new_tags = input("Enter new tags separated by commas: ").strip()
        new_tags = new_tags.split(",")
        new_tags = [t.strip() for t in new_tags if t.strip()]
        for t in new_tags:
            if t not in tags and t.isalnum():
                tags.append(t)
        return tags

    def refresh_tokens(self):
        logging.debug("Refreshing Channel Updater tokens")
        twitch_refresh_url = str(
            f"https://id.twitch.tv/oauth2/token?"
            f"grant_type=refresh_token&"
            f"refresh_token={self.refresh_token}&"
            f"client_id={self.client_id}&"
            f"client_secret={self.client_secret}"
        )
        refresh = DotMap(httpx.post(twitch_refresh_url).json())
        logging.debug(f"Refresh response: {refresh}")
        if self.access_token != refresh.access_token:
            ConfigController.update_config_file(
                self.config_file,
                "auth",
                "channel_update_access_token",
                refresh.access_token,
            )
            self.access_token = refresh.access_token

        if self.refresh_token != refresh.refresh_token:
            ConfigController.update_config_file(
                self.config_file,
                "auth",
                "channel_update_refresh_token",
                refresh.refresh_token,
            )
            self.refresh_token = refresh.refresh_token
        self.update_headers()
        logging.info("Refreshed Twitch Chat Tokens")
        return True
