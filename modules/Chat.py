import json
import re
import requests
import logging
from dotmap import DotMap
import twitchio
from twitchio.ext import commands, eventsub
import datetime
from AsyncioThread import AsyncioThread
from helpers.AbstractModule import BotdeliciousModule
from helpers.ConfigManager import ConfigManager
from helpers.Enums import ModuleStatus
from helpers.SessionData import SessionData
from modules.Event import EventModule
from modules.cogs.Commands import CommandsCog


class _TwitchBot(commands.Bot):
    def __init__(self, config):
        logging.info(f"Starting Twitch chat bot")
        self.config = config
        super().__init__(
            token=self.config.access_token,
            prefix=self.config.bot_prefix,
            initial_channels=self.config.channels,
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            case_insensitive=True,
        )

        self.event_subscription = eventsub.EventSubClient(
            self, self.config.event_sub.secret, self.config.event_sub.callback
        )

        self.add_cog(CommandsCog(self))

    async def event_ready(self):
        logging.info(f"Logged in as | {self.nick}")
        logging.info(f"User id is | {self.user_id}")
        await self.event_subscription.listen(
            port=self.config.event_sub.listen_port
        )
        await self.say_hello()

    async def event_message(self, message):
        AsyncioThread.run_coroutine(
            EventModule.queue_event(event="new_message")
        )

        if message.author.name in self.config.moderators:
            await self.moderator_active(message.author.name)

        if message.author.name in self.config.vips:
            await self.vip_active(message.author.name)

        if message.content[0] == self.config.bot_prefix:
            await self.handle_commands(message)
            return

    async def moderator_active(self, moderator):
        if moderator not in SessionData.get_moderators():
            SessionData.add_moderator(moderator=moderator)
            AsyncioThread.run_coroutine(
                EventModule.queue_event(event="moderator", moderator=moderator)
            )

    async def vip_active(self, vip):
        if vip not in SessionData.get_vips():
            SessionData.add_vip(vip=vip)
            AsyncioThread.run_coroutine(
                EventModule.queue_event(event="vip", vip=vip)
            )

    async def event_eventsub_notification_follow(
        self, payload: eventsub.ChannelFollowData
    ):
        logging.debug(f"New follower!")
        logging.debug(payload.data.user.name)
        SessionData.add_follower(follower=payload.data.user.name)
        AsyncioThread.run_coroutine(
            EventModule.queue_event(
                event="new_follower", username=payload.data.user.name
            )
        )

    async def event_eventsub_notification_raid(
        self, payload: eventsub.ChannelRaidData
    ):
        logging.debug(f"New raid!")
        logging.debug(payload.data.raider.name)
        logging.debug(payload.data.viewer_count)
        SessionData.add_raid(
            raider=payload.data.raider.name, size=payload.data.viewer_count
        )
        AsyncioThread.run_coroutine(
            EventModule.queue_event(
                event="raid",
                name=payload.data.raider.name,
                count=payload.data.viewer_count,
            )
        )

    async def send_message_to_channel(self, channel, message):
        chan = self.get_channel(channel)
        self.loop.create_task(chan.send(message))

    async def say_hello(self):
        for channel in self.connected_channels:
            current_time_string = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            await self.send_message_to_channel(
                channel.name, f"Hello World! ({current_time_string})"
            )

    async def say_bye(self):
        for channel in self.connected_channels:
            current_time_string = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            await self.send_message_to_channel(
                channel.name, f"Bye World! ({current_time_string})"
            )

    def find_username(self, message):
        res = re.search("@(\w+)", message)
        if not res:
            res = message.split(" ")
            try:
                return res[1]
            except IndexError:
                return False
        return res.group(1)

    async def fetch_user_info(self, username):
        fetch_url = f"https://api.twitch.tv/helix/users?login={username}"
        headers = {
            "Client-Id": f"{self.config.client_id}",
            "Authorization": f"Bearer {self.config.access_token}",
        }
        response = requests.get(url=fetch_url, headers=headers)
        return json.loads(response.content)["data"][0]["profile_image_url"]


class ChatModule(BotdeliciousModule):
    def __init__(self):
        super().__init__()

    async def start(self):
        self.set_status(ModuleStatus.RUNNING)
        self.config = ConfigManager.get("chat")
        await self._update_tokens()
        self.bot = _TwitchBot(self.config)
        self.bot.run()

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        await self.bot.say_bye()
        await self.bot.close()
        self.set_status(ModuleStatus.IDLE)

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
