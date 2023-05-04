import logging
import openai
from openai import OpenAIError
from Controllers.ConfigController import ConfigController
from Helpers.SessionData import SessionData

from Modules.BotdeliciousModule import BotdeliciousModule
from Helpers.Dataclasses import ConversationEntry
from Helpers.Enums import ConversationStatus, ModuleStatus
from Helpers.Utilities import Utilities


class OpenaiModule(BotdeliciousModule):
    _conversations = {}
    _conversation_status = {}
    _prompt = ""
    _thinking_message = ""
    _error_message = ""

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def set_config(cls, config):
        cls.prompt = config.prompt
        cls.thinking_message = config.thinking_message
        cls.error_message = config.error_message

    async def start(self):
        config = ConfigController.get("openai")
        openai.organization = config.org
        openai.api_key = config.key
        self.set_config(config)
        self.set_status(ModuleStatus.RUNNING)

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        self.set_status(ModuleStatus.IDLE)

    @classmethod
    def start_conversation(cls, conversation_group):
        cls._conversations[conversation_group] = [
            ConversationEntry(
                "system",
                cls._prompt.format(conversation_group=conversation_group),
                "niddelicious",
            )
        ]
        cls._conversation_status[conversation_group] = ConversationStatus.IDLE

    @classmethod
    def reprompt_conversation(cls, conversation_group, prompt: str = None):
        cls.clean_conversation(conversation_group)
        conversation_prompt = (
            prompt
            if prompt
            else cls._prompt.format(conversation_group=conversation_group)
        )
        cls._conversations[conversation_group] = [
            ConversationEntry("system", conversation_prompt, "niddelicious")
        ]
        cls._conversation_status[conversation_group] = ConversationStatus.IDLE

    @classmethod
    def clean_conversation(cls, conversation_group):
        if conversation_group in cls._conversations:
            del cls._conversations[conversation_group]
        if conversation_group in cls._conversation_status:
            del cls._conversation_status[conversation_group]

    @classmethod
    def add_message(cls, conversation_group, username, message):
        cls._conversations[conversation_group].append(
            ConversationEntry("user", message, username)
        )
        if len(cls._conversations[conversation_group]) > 15:
            del cls._conversations[conversation_group][1:3]

    @classmethod
    def add_reply(cls, conversation_group, reply):
        cls._conversations[conversation_group].append(
            ConversationEntry("assistant", reply, "botdelicious")
        )

    @classmethod
    def get_conversation(cls, conversation_group):
        logging.debug(cls._conversations[conversation_group])
        return cls._conversations[conversation_group]

    @classmethod
    def get_conversation_status(cls, conversation_group):
        if conversation_group not in cls._conversation_status:
            cls.start_conversation(conversation_group)
        logging.debug(
            f"Conversation status for {conversation_group} is {cls._conversation_status[conversation_group]}"
        )
        return cls._conversation_status[conversation_group]

    @classmethod
    def set_conversation_status(cls, conversation_group, status):
        cls._conversation_status[conversation_group] = status

    @classmethod
    async def request_chat(cls, messages):
        """
        $0.002 per 1000 tokens using gpt-3.5-turbo
        Which is 1/10th of the cost of text-davinci-003
        Meaning that even with a larger prompt, this is still cheaper
        """
        try:
            json_messages = [message.__dict__ for message in messages]
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=json_messages,
            )
            logging.info(response)
            return response
        except OpenAIError as e:
            logging.error(e)
            return False

    @classmethod
    async def request_text(cls, prompt: str = None, chaos: float = 1.0):
        """
        $0.020 per 1000 tokens using text-davinci-003
        Which means 10x that of gpt-3.5-turbo
        So rather use that than this
        """
        try:
            response = await openai.Completion.acreate(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=100,
                temperature=chaos,
            )
            logging.info(response)
            return response
        except OpenAIError as e:
            logging.error(e)
            return False

    @classmethod
    async def chat(
        cls, channel: str = None, username: str = None, message: str = None
    ):
        if cls.get_status() != ModuleStatus.RUNNING:
            return False
        if cls.get_conversation_status(channel) == ConversationStatus.IDLE:
            cls.set_conversation_status(channel, ConversationStatus.OCCUPIED)
            cls.add_message(channel, username, message)
            response = await cls.request_chat(cls.get_conversation(channel))
            if response:
                SessionData.add_tokens(
                    tokens=int(response["usage"]["total_tokens"])
                )
                reply = response["choices"][0]["message"]["content"]
                cls.add_reply(channel, reply)
            else:
                reply = cls._error_message.format(username=username)
            cls.set_conversation_status(channel, ConversationStatus.IDLE)
        else:
            reply = cls._thinking_message.format(username=username)
        return reply

    @classmethod
    async def shoutout(cls, content: str = None, author: str = None):
        """
        Returns success, username, reply, and avatar_url
        Or None, None, None, None if the module is not running
        """
        if cls.get_status() != ModuleStatus.RUNNING:
            return None, None, None, None

        system_name = "ai_shoutout_generator"
        system_prompt = "Hype Twitch Streamer Shoutout Generator"
        twitch_config = ConfigController.get("chat")
        username = Utilities.find_username(content)
        if username:
            user = await Utilities.get_user_info(
                username=username,
                client_id=twitch_config.client_id,
                access_token=twitch_config.access_token,
            )
        else:
            user = None
            username = None
        if not user:
            system_prompt = "Hype Twitch Streamer Shoutout Generator"
            system_message = f"Give a snarky reply about how @{author} tried to shoutout @{username}, but that user doesn't exist."
            avatar_url = None
            success = False
        else:
            user_id = user["id"]
            avatar_url = user["profile_image_url"]
            user_description = user["description"]
            channel_info = await Utilities.get_channel_info(
                user_id=user_id,
                client_id=twitch_config.client_id,
                access_token=twitch_config.access_token,
            )
            game_name = channel_info["game_name"]
            title = channel_info["title"]
            tags = channel_info["tags"]
            stream_info = await Utilities.get_live_stream_info(
                user_id=user_id,
                client_id=twitch_config.client_id,
                access_token=twitch_config.access_token,
            )
            live_message = (
                "is currently live and is"
                if stream_info
                else "is currently not live, but was last seen"
            )
            system_message = f"Write a shoutout for a Twitch streamer named {username} who {live_message} playing {game_name} with the stream title {title}. This is their description: {user_description}.  These are their tags: {tags}. Do not list the tags in the reply. Make sure to end the reply with their url: https://twitch.tv/{username}. Keep the reply under 490 characters."
            success = True

        # If using completion instead of chat
        # response = await self.request_chat(prompt=system_message)
        # reply = response["choices"][0]["text"]

        # If using chat instead of completion
        cls.reprompt_conversation(system_name, system_prompt)
        cls.add_message(system_name, "niddelicious", system_message)
        response = await cls.request_chat(cls.get_conversation(system_name))
        reply = response["choices"][0]["message"]["content"]

        SessionData.add_tokens(tokens=int(response["usage"]["total_tokens"]))
        return success, username, reply, avatar_url
