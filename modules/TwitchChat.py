import requests
import logging
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
        self.run()

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
        logging.info(self.Bot.config.twitch.accessToken)
        logging.info(self.Bot.config.twitch.refreshToken)
        logging.info(self.Bot.config.twitch.clientId)
        logging.info(self.Bot.config.twitch.clientSecret)
        twitchRefreshUrl = str(
            f"https://id.twitch.tv/oauth2/token?grant_type=refresh_token&refresh_token={self.Bot.config.twitch.refreshToken}&client_id={self.Bot.config.twitch.clientId}&client_secret={self.Bot.config.twitch.clientSecret}"
        )
        refresh = requests.post(twitchRefreshUrl)
        refresh_response = refresh.json()
        logging.info(f"Refresh response: {refresh_response}")

        accessToken = refresh_response["access_token"]
        refreshToken = refresh_response["refresh_token"]
        if self.Bot.config.twitch.accessToken != accessToken:
            self.Bot.updateConfig("twitch", "accessToken", accessToken)

        if self.Bot.config.twitch.refreshToken != refreshToken:
            self.Bot.updateConfig("twitch", "refreshToken", refreshToken)

        logging.info("Refreshed tokens")
