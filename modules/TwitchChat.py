import requests
import logging
from dotmap import DotMap
from twitchio.ext import commands
import datetime
from helpers.AbstractModule import BotdeliciousModule
from helpers.ConfigManager import ConfigManager
from helpers.Enums import ModuleStatus


class TwitchChat(commands.Bot, BotdeliciousModule):
    def init(self):
        self.update_tokens()
        super().init(
            token=ConfigManager.config.twitch.access_token,
            prefix=ConfigManager.config.twitch.bot_prefix,
            initial_channels=ConfigManager.config.twitch.channels,
            client_id=ConfigManager.config.twitch.client_id,
            client_secret=ConfigManager.config.twitch.client_secret,
            case_insensitive=True,
        )
        self.status = ModuleStatus.IDLE

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")
        for channel in self.connected_channels:
            current_time_string = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            await self.send_message_to_chat(
                channel.name, f"Hello World! ({current_time_string})"
            )

    async def send_message_to_chat(self, channel, message):
        chan = self.get_channel(channel)
        self.loop.create_task(chan.send(message))

    def update_tokens(self):
        logging.debug("Refreshing token")
        twitch_refresh_url = str(
            f"https://id.twitch.tv/oauth2/token?"
            f"grant_type=refresh_token&"
            f"refresh_token={ConfigManager.config.twitch.refresh_token}&"
            f"client_id={ConfigManager.config.twitch.client_id}&"
            f"client_secret={ConfigManager.config.twitch.client_secret}"
        )
        refresh = DotMap(requests.post(twitch_refresh_url).json())
        logging.debug(f"Refresh response: {refresh}")
        if ConfigManager.config.twitch.access_token != refresh.access_token:
            ConfigManager.update_config(
                "twitch", "access_token", refresh.access_token
            )

        if ConfigManager.config.twitch.refresh_token != refresh.refresh_token:
            ConfigManager.update_config(
                "twitch", "refresh_token", refresh.refresh_token
            )

        logging.info("Refreshed Twitch Tokens")

    def start(self):
        self.status = ModuleStatus.RUNNING
        self.run()

    def stop(self):
        self.status = ModuleStatus.STOPPING
        self.close()
        self.status = ModuleStatus.IDLE

    def status(self):
        return self.status
