import requests
import logging
from dotmap import DotMap
from twitchio.ext import commands
import datetime

from helpers.ConfigManager import ConfigManager


class TwitchChat(commands.Bot):
    def __init__(self, parent):
        self.parent = parent
        self.updateTokens()
        super().__init__(
            token=ConfigManager.config.twitch.accessToken,
            prefix=ConfigManager.config.twitch.botPrefix,
            initial_channels=ConfigManager.config.twitch.channels,
            client_id=ConfigManager.config.twitch.clientId,
            client_secret=ConfigManager.config.twitch.clientSecret,
            case_insensitive=True,
        )

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")
        for channel in self.connected_channels:
            current_time_string = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            await self.sendMessageToChat(
                channel.name, f"Hello World! ({current_time_string})"
            )

    async def sendMessageToChat(self, channel, message):
        chan = self.get_channel(channel)
        self.loop.create_task(chan.send(message))

    def updateTokens(self):
        logging.debug("Refreshing token")
        twitchRefreshUrl = str(
            f"https://id.twitch.tv/oauth2/token?"
            f"grant_type=refresh_token&"
            f"refresh_token={ConfigManager.config.twitch.refreshToken}&"
            f"client_id={ConfigManager.config.twitch.clientId}&"
            f"client_secret={ConfigManager.config.twitch.clientSecret}"
        )
        refresh = DotMap(requests.post(twitchRefreshUrl).json())
        logging.debug(f"Refresh response: {refresh}")
        if ConfigManager.config.twitch.accessToken != refresh.access_token:
            ConfigManager.update_config(
                "twitch", "accessToken", refresh.access_token
            )

        if ConfigManager.config.twitch.refreshToken != refresh.refresh_token:
            ConfigManager.update_config(
                "twitch", "refreshToken", refresh.refresh_token
            )

        logging.info("Refreshed Twitch Tokens")
