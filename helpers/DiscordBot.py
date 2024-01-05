from typing import Any
import discord

import logging

from discord.flags import Intents

from Controllers.ConfigController import ConfigController


class DiscordBot:
    TOKEN = None
    CHANNEL_ID = None
    BOT = None

    @classmethod
    async def upload(cls, filename: str = None, prompt: str = None, author: str = None):
        logging.debug(f"Configuring DiscordClient")
        config = ConfigController.get("discord")
        cls.TOKEN = config.token
        cls.CHANNEL_ID = config.channel_id

        intents = discord.Intents.default()
        intents.message_content = True

        logging.debug(f"Creating DiscordClient")
        cls.BOT = DiscordClient(intents=intents, channel_id=cls.CHANNEL_ID)
        cls.BOT.post_filename = filename
        cls.BOT.post_prompt = prompt
        cls.BOT.post_author = author

        logging.debug(f"Connecting DiscordClient...")
        await cls.BOT.start(cls.TOKEN)


class DiscordClient(discord.Client):
    def __init__(
        self, *, intents: Intents, channel_id: int = None, **options: Any
    ) -> None:
        super().__init__(intents=intents, **options)
        self.channel_id = channel_id
        self.post_filename = None
        self.post_prompt = None
        self.post_author = None

    async def on_ready(self):
        logging.debug(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.upload()

    async def upload(self):
        logging.debug(f"Uploading to Discord...")
        channel = self.get_channel(self.channel_id)

        logging.debug(f"Sending message to Discord...")

        message = f"{self.post_author} ordered '{self.post_prompt}': https://nidde.nu/gallery/{self.post_filename}"
        await channel.send(message)

        with open("stable-diffusion.png", "rb") as file:
            file_data = discord.File(file, filename=f"{self.post_filename}.png")
            await channel.send(file=file_data)

        logging.info(f"Sent '{message}' to Discord!")
        await self.close()
