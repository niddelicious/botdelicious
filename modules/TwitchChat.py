import requests
import logging
from dotmap import DotMap
from twitchio.ext import commands
import datetime


class TwitchChat(commands.Bot):
    def __init__(self, parent):
        self.parent = parent
        self.updateTokens()
        super().__init__(
            token=self.parent.config.twitch.accessToken,
            prefix=self.parent.config.twitch.botPrefix,
            initial_channels=self.parent.config.twitch.channels,
            client_id=self.parent.config.twitch.clientId,
            client_secret=self.parent.config.twitch.clientSecret,
            case_insensitive=True,
        )

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")
        for channel in self.connected_channels:
            current_time_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await self.sendMessageToChat(
                channel.name, f"Hello World! ({current_time_string})"
            )

    async def sendMessageToChat(self, channel, message):
        chan = self.get_channel(channel)
        self.loop.create_task(chan.send(message))

    def updateTokens(self):
        logging.debug("Refreshing token")
        twitchRefreshUrl = str(
            f"https://id.twitch.tv/oauth2/token?grant_type=refresh_token&refresh_token={self.parent.config.twitch.refreshToken}&client_id={self.parent.config.twitch.clientId}&client_secret={self.parent.config.twitch.clientSecret}"
        )
        refresh = DotMap(requests.post(twitchRefreshUrl).json())
        logging.debug(f"Refresh response: {refresh}")
        if self.parent.config.twitch.accessToken != refresh.access_token:
            self.parent.configManager.updateConfig(
                "twitch", "accessToken", refresh.access_token
            )

        if self.parent.config.twitch.refreshToken != refresh.refresh_token:
            self.parent.configManager.updateConfig(
                "twitch", "refreshToken", refresh.refresh_token
            )

        logging.info("Refreshed Twitch Tokens")
