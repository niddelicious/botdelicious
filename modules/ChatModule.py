import asyncio
import json
import random
import re
import requests
import logging
from dotmap import DotMap
from twitchio.ext import commands, eventsub
import datetime
from AsyncioThread import AsyncioThread
from Modules.BotdeliciousModule import BotdeliciousModule
from Controllers.ConfigController import ConfigController
from Helpers.Enums import ModuleStatus
from Helpers.SessionData import SessionData
from Modules.Cogs.EventCog import EventCog
from Modules.Cogs.LightsCog import LightsCog
from Modules.Cogs.PublicAnnouncementCog import PublicAnnouncementCog
from Modules.EventModule import EventModule
from Modules.Cogs.CommandsCog import CommandsCog
from Modules.OpenaiModule import OpenaiModule
from Modules.Cogs.ShotsCog import ShotsCog
from Modules.Cogs.CharityCog import CharityCog
from Modules.Cogs.AdminCog import AdminCog
from Modules.Cogs.NFTCog import NFTCog
from Modules.WebsocketModule import WebsocketModule
import os


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
            client=self,
            webhook_secret=self.config.event_sub.secret,
            callback_route=self.config.event_sub.callback,
            token=self.config.access_token,
        )

        self._pattern = rf".*{self.config.bot_name}.*"
        # self.add_cog(CommandsCog(bot=self))
        # self.add_cog(ShotsCog())
        # self.add_cog(LightsCog())
        # self.add_cog(EventCog())
        # self.add_cog(CharityCog())
        # self.add_cog(PublicAnnouncementCog(bot=self))
        self.add_cog(AdminCog())
        self.add_cog(NFTCog(bot=self))

        if self.config.log_to_file:
            self.init_log_file()

    async def event_ready(self):
        logging.info(f"Logged in as | {self.nick}")
        logging.info(f"User id is | {self.user_id}")
        AsyncioThread.run_coroutine(
            self.event_subscription.listen(port=self.config.event_sub.listen_port)
        )
        await self.say_hello()

    async def event_message(self, message):
        if self.config.log_to_file:
            await self.log_chat(message)
            await self.serve_message(message)

        if message.echo:
            return

        AsyncioThread.run_coroutine(EventModule.queue_event(event="new_message"))
        logging.info(f"{message.author.name}: {message.content}")

        if message.author.is_mod:
            await self.moderator_active(message.author.name)
        elif message.author.is_vip:
            await self.vip_active(message.author.name)
        else:
            await self.chatter_active(message.author.name)

        if re.match(self._pattern, message.content):
            reply = await OpenaiModule.chat(
                channel=message.channel.name,
                username=message.author.name,
                message=message.content,
            )
            if reply:
                await self.send_message_to_channel(message.channel.name, reply)
            return

        if message.content[0] == self.config.bot_prefix:
            await self.handle_commands(message)
            return

    @classmethod
    async def moderator_active(cls, moderator):
        if moderator not in SessionData.get_moderators():
            SessionData.add_moderator(moderator=moderator)
            AsyncioThread.run_coroutine(
                EventModule.queue_event(event="moderator", moderator=moderator)
            )

    @classmethod
    async def vip_active(cls, vip):
        if vip not in SessionData.get_vips():
            SessionData.add_vip(vip=vip)
            AsyncioThread.run_coroutine(EventModule.queue_event(event="vip", vip=vip))

    @classmethod
    async def chatter_active(cls, chatter):
        if chatter not in SessionData.get_chatters():
            SessionData.add_chatter(chatter=chatter)
            AsyncioThread.run_coroutine(
                EventModule.queue_event(event="chatter", chatter=chatter)
            )

    async def event_eventsub_notification_followV2(
        self, payload: eventsub.ChannelFollowData
    ):
        logging.warning(f"New follower! (v2)")
        logging.warning(payload)
        logging.warning(payload.data.user.name)
        SessionData.add_follower(follower=payload.data.user.name)
        avatar_url = await self.fetch_user_avatar(payload.data.user.name)
        AsyncioThread.run_coroutine(
            EventModule.queue_event(
                event="new_follower",
                username=payload.data.user.name,
                avatar_url=avatar_url,
            )
        )
        message = await OpenaiModule.event_intepretor(
            f"@{payload.data.user.name} followed"
        )
        await self.send_message_to_channel(
            channel="niddelicious",
            message=message,
        )

    async def event_eventsub_notification_raid(self, payload: eventsub.ChannelRaidData):
        logging.debug(f"New raid!")
        logging.debug(payload.data.raider.name)
        logging.debug(payload.data.viewer_count)
        SessionData.add_raid(
            raider=payload.data.raider.name, size=payload.data.viewer_count
        )
        avatar_url = await self.fetch_user_avatar(payload.data.raider.name)
        AsyncioThread.run_coroutine(
            EventModule.queue_event(
                event="raid",
                name=payload.data.raider.name,
                count=payload.data.viewer_count,
                avatar_url=avatar_url,
            )
        )
        message = await OpenaiModule.event_intepretor(
            f"@{payload.data.raider.name} raided "
            f"with {payload.data.viewer_count} friends"
        )
        await self.send_message_to_channel(
            channel="niddelicious",
            message=message,
        )

    async def chat(self, channel, message):
        if len(message) > 500:
            await self.send_message_to_channel(channel, message)
        else:
            await self.get_channel(channel).send(message)

    async def send_message_to_channel(self, channel, message):
        chan = self.get_channel(channel)

        # Split the message into chunks of up to 500 characters
        message_chunks = []
        while message:
            if len(message) > 500:
                last_space_or_punctuation = re.search(
                    r"[\s\.,;!?-]{1,}[^\s\.,;!?-]*$", message[:500]
                )
                if last_space_or_punctuation:
                    split_at = last_space_or_punctuation.start()
                else:
                    split_at = 500

                chunk = message[:split_at]
                message = message[split_at:].lstrip()
            else:
                chunk = message
                message = ""

            message_chunks.append(chunk)

        # Send each chunk as a separate message
        for chunk in message_chunks:
            self.loop.create_task(chan.send(chunk))
            await asyncio.sleep(2)

    async def say_everywhere(self, message):
        for channel in self.connected_channels:
            await self.send_message_to_channel(channel.name, message)

    async def say_hello(self):
        for channel in self.connected_channels:
            current_time_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await self.send_message_to_channel(
                channel.name, f"Hello World! ({current_time_string})"
            )

    async def say_bye(self):
        for channel in self.connected_channels:
            current_time_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await self.send_message_to_channel(
                channel.name, f"Bye World! ({current_time_string})"
            )

    async def fetch_user_avatar(self, username):
        fetch_url = f"https://api.twitch.tv/helix/users?login={username}"
        headers = {
            "Client-Id": f"{self.config.client_id}",
            "Authorization": f"Bearer {self.config.access_token}",
        }
        response = requests.get(url=fetch_url, headers=headers)
        content = json.loads(response.content)
        if len(content["data"]) < 1:
            logging.warning(
                f"Could not fetch avatar for user {username}. " f"Response: {content}"
            )
            return await self.fetch_user_avatar("botdelicious")
        return json.loads(response.content)["data"][0]["profile_image_url"]

    def init_log_file(self):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.log_filename = f"chatlogs/{current_date}.log"
        self.nft_log_filename = f"chatlogs/nft_chat.log"

    async def log_chat(self, message):
        author = self.config.bot_name if message.echo else message.author.name
        current_time_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        short_time_string = datetime.datetime.now().strftime("%H:%M")
        with open(self.log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(f"{current_time_string} | {author}: {message.content}\n")
        with open(self.nft_log_filename, "a", encoding="utf-8") as nft_file:
            nft_file.write(
                f"{short_time_string} {message.channel.name} | {author}: {message.content}\n"
            )

    async def serve_message(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        channel = message.channel.name
        author = self.config.bot_name if message.echo else message.author.name
        message = message.content
        payload = {
            "timestamp": timestamp,
            "channel": channel,
            "author": author,
            "message": message,
        }
        await WebsocketModule.send_websocket_message(payload)


class ChatModule(BotdeliciousModule):
    _bot: _TwitchBot

    def __init__(self):
        super().__init__()

    async def start(self):
        self.set_status(ModuleStatus.RUNNING)
        self.config = ConfigController.get("chat")
        await self._update_tokens()
        self.bot = _TwitchBot(self.config)
        self.set_bot(self.bot)
        await self.bot.start()

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        await self.bot.say_bye()
        await self.bot.close()
        self.set_status(ModuleStatus.IDLE)

    @classmethod
    def get_bot(cls):
        return cls._bot

    @classmethod
    def set_bot(cls, bot):
        cls._bot = bot

    @classmethod
    async def send_message(cls, message):
        await cls._bot.say_everywhere(message)

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
            ConfigController.update_config("chat", "access_token", refresh.access_token)

        if self.config.refresh_token != refresh.refresh_token:
            ConfigController.update_config(
                "chat", "refresh_token", refresh.refresh_token
            )

        logging.info("Refreshed Twitch Chat Tokens")
        return True
