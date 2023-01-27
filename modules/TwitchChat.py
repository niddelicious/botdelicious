import requests
import logging
from dotmap import DotMap
from twitchio.ext import commands


class TwitchChat(commands.Bot):
    def __init__(self, Bot=None):

        self.Bot = Bot
        self.updateTokens()
        super().__init__(
            token=self.Bot.config.twitch.accessToken,
            prefix=self.Bot.config.twitch.botPrefix,
            initial_channels=self.Bot.config.twitch.channels,
            client_id=self.Bot.config.twitch.clientId,
            client_secret=self.Bot.config.twitch.clientSecret,
            case_insensitive=True,
        )

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")
        for channel in self.connected_channels:
            await self.sendMessageToChat(channel.name, "Hello World!")

    async def sendMessageToChat(self, channel, message):
        chan = self.get_channel(channel)
        self.loop.create_task(chan.send(message))

    def updateTokens(self):
        logging.info("Refreshing token")
        twitchRefreshUrl = str(
            f"https://id.twitch.tv/oauth2/token?grant_type=refresh_token&refresh_token={self.Bot.config.twitch.refreshToken}&client_id={self.Bot.config.twitch.clientId}&client_secret={self.Bot.config.twitch.clientSecret}"
        )
        refresh = DotMap(requests.post(twitchRefreshUrl).json())
        logging.info(f"Refresh response: {refresh}")
        if self.Bot.config.twitch.accessToken != refresh.access_token:
            self.Bot.updateConfig("twitch", "accessToken", refresh.access_token)

        if self.Bot.config.twitch.refreshToken != refresh.refresh_token:
            self.Bot.updateConfig("twitch", "refreshToken", refresh.refresh_token)

        logging.info("Refreshed tokens")
