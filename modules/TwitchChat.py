from twitchio.ext import commands


class TwitchChat(commands.Bot):
    def __init__(self, config):
        super().__init__(
            token=config.accessToken,
            prefix=config.botPrefix,
            initial_channels=config.channels,
            client_id=config.clientId,
            client_secret=config.clientSecret,
            case_insensitive=True,
        )

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")
        await self.sendMessageToChat("niddelicious", "Hello World!")

    async def sendMessageToChat(self, channel, message):
        chan = self.get_channel(channel)
        self.loop.create_task(chan.send(message))
