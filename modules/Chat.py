import requests
import logging
from dotmap import DotMap
from twitchio.ext import commands
import datetime
from helpers.AbstractModule import BotdeliciousModule
from helpers.ConfigManager import ConfigManager
from helpers.Enums import ModuleStatus
from modules.cogs.Commands import CommandsCog


class _TwitchBot(commands.Bot):
    def __init__(self, config):
        logging.info(f'Starting Twitch chat bot')
        self.config = config
        super().__init__(
            token=self.config.access_token,
            prefix=self.config.bot_prefix,
            initial_channels=self.config.channels,
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            case_insensitive=True,
        )

        self.add_cog(CommandsCog(self))

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")
        for channel in self.connected_channels:
            current_time_string = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            await self.send_message_to_channel(
                channel.name, f"Hello World! ({current_time_string})"
            )

    async def send_message_to_channel(self, channel, message):
        chan = self.get_channel(channel)
        self.loop.create_task(chan.send(message))


class ChatModule(commands.Bot, BotdeliciousModule):
    _status = ModuleStatus.IDLE

    def __init__(self):
        self._status = ModuleStatus.IDLE

    async def start(self):
        self._status = ModuleStatus.RUNNING
        self.config = ConfigManager.get("chat")
        await self._update_tokens()
        self.bot = _TwitchBot(self.config)
        self.bot.run()

    async def stop(self):
        self._status = ModuleStatus.STOPPING
        self.close()
        self._status = ModuleStatus.IDLE

    async def status(self):
        return self._status

    async def _update_tokens(self):
        logging.debug("Refreshing Twitch Chat tokens")
        twitch_refresh_url = str(
            f"https://id.twitch.tv/oauth2/token?"
            f"grant_type=refresh_token&"
            f"refresh_token={self.config.refresh_token}&"
            f"client_id={self.config.client_id}&"
            f"client_secret={self.config.client_secret}"
        )
        refresh = DotMap(requests.post(twitch_refresh_url).json())
        logging.debug(f"Refresh response: {refresh}")
        if self.config.access_token != refresh.access_token:
            ConfigManager.update_config(
                "chat", "access_token", refresh.access_token
            )

        if self.config.refresh_token != refresh.refresh_token:
            ConfigManager.update_config(
                "chat", "refresh_token", refresh.refresh_token
            )

        logging.info("Refreshed Twitch Chat Tokens")
        return True
