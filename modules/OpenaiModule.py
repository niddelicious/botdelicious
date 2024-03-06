import logging
import datetime
import openai
from openai import OpenAIError
from Controllers.ConfigController import ConfigController
from Helpers.SessionData import SessionData

from Modules.BotdeliciousModule import BotdeliciousModule
from Helpers.Dataclasses import ConversationEntry
from Helpers.Enums import ConversationStatus, ModuleStatus, QueueStatus
from Helpers.Utilities import Utilities


class OpenaiModule(BotdeliciousModule):
    _conversations = {}
    _conversation_status = {}
    _prompt = ""
    _thinking_message = ""
    _error_message = ""
    _model = ""
    _image_status: QueueStatus = QueueStatus.IDLE
    _logger = None

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def set_config(cls, config):
        cls._prompt = config.prompt
        cls._thinking_message = config.thinking_message
        cls._error_message = config.error_message
        cls._model = config.model

    async def start(self):
        config = ConfigController.get("openai")
        openai.organization = config.org
        openai.api_key = config.key
        self.set_config(config)
        await self.openai_logging()
        self.set_status(ModuleStatus.RUNNING)

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        self.set_status(ModuleStatus.IDLE)

    @classmethod
    async def openai_logging(cls):
        cls._logger = logging.getLogger(__name__)
        cls._logger.setLevel(logging.DEBUG)
        cls._logger.propagate = False
        log_filename = datetime.datetime.now().strftime(
            f"logs/{__name__}-%Y-%m-%d_%H-%M-%S.log"
        )
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s", "%m-%d-%Y %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        cls._logger.addHandler(file_handler)

    @classmethod
    def start_conversation(cls, conversation_group):
        cls._conversations[conversation_group] = [
            ConversationEntry(
                "system",
                cls._prompt.format(conversation_group=conversation_group),
                "Twitch",
            )
        ]
        cls._conversation_status[conversation_group] = ConversationStatus.IDLE

    @classmethod
    def reprompt_conversation(cls, conversation_group, prompt: str = None):
        cls.clean_conversation(conversation_group)
        conversation_prompt = (
            prompt if prompt else cls._prompt.format(username=conversation_group)
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
    def add_message(cls, conversation_group, username, message, role: str = "user"):
        cls._conversations[conversation_group].append(
            ConversationEntry(role, message, username)
        )
        if len(cls._conversations[conversation_group]) > 100:
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
            f"Conversation status for {conversation_group}"
            f" is {cls._conversation_status[conversation_group]}"
        )
        return cls._conversation_status[conversation_group]

    @classmethod
    def set_conversation_status(cls, conversation_group, status):
        cls._conversation_status[conversation_group] = status

    @classmethod
    async def request_chat(
        cls, messages, assistant_message: str = None, chaos: float = 1.0
    ):
        try:
            cls._logger.warning("New query:")
            json_messages = [message.__dict__ for message in messages]
            if assistant_message:
                json_messages.append(assistant_message.__dict__)
            cls._logger.info(json_messages)
            response = await openai.ChatCompletion.acreate(
                model=cls._model,
                messages=json_messages,
                temperature=chaos,
            )
            logging.info(response)
            cls._logger.info(response)
            return response
        except OpenAIError as e:
            logging.error(e)
            return False

    @classmethod
    async def chat(cls, channel: str = None, username: str = None, message: str = None):
        if cls.get_status() != ModuleStatus.RUNNING:
            return f"💤"
        if cls.get_conversation_status(channel) == ConversationStatus.IDLE:
            cls.set_conversation_status(channel, ConversationStatus.OCCUPIED)
            cls.add_message(channel, username, message)
            assistant_message = ConversationEntry(
                "assistant",
                f"Please respond to @{username}'s last message: '{message}'."
                f" Consider the context and adress them directly.",
                "Twitch",
            )
            response = await cls.request_chat(
                cls.get_conversation(channel),
                assistant_message=assistant_message,
            )
            if response:
                SessionData.add_tokens(tokens=int(response["usage"]["total_tokens"]))
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
            user = await Utilities.get_twitch_user_info(username=username)
        else:
            user = None
            username = None
        if not user:
            system_prompt = "Hype Twitch Streamer Shoutout Generator"
            system_message = (
                f"Give a snarky reply about how @{author}"
                f" tried to shoutout @{username}, but that user doesn't exist."
            )
            avatar_url = None
            success = False
        else:
            user_id = user["id"]
            avatar_url = user["profile_image_url"]
            user_description = user["description"]
            channel_info = await Utilities.get_twitch_channel_info(user_id=user_id)
            game_name = channel_info["game_name"]
            title = channel_info["title"]
            tags = channel_info["tags"]
            stream_info = await Utilities.get_twitch_live_stream_info(user_id=user_id)
            live_message = (
                "is currently live and is"
                if stream_info
                else "is currently not live, but was last seen"
            )
            system_message = (
                f"Write a shoutout for a Twitch streamer named {username}"
                f"who {live_message} playing {game_name}"
                f" with the stream title {title}."
                f"This is their description: {user_description}."
                f"These are their tags: {tags}."
                f"Do not list the tags in the reply."
                f"Make sure to end the reply with their url:"
                f"https://twitch.tv/{username}."
                f"Keep the reply under 490 characters."
            )
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

    @classmethod
    async def rgb_intepretor(cls, content: str = None, author: str = None):
        if cls.get_status() != ModuleStatus.RUNNING:
            return None

        system_name = "ai_rgb_color_converter"
        system_prompt = (
            "You are a RGB color converting bot,"
            " taking a description and translating it"
            "to a json format:"
            "{'red': value_red, 'green': value_green, 'blue': value_blue}."
            "Do not answer in any other way."
            "If no color is appropriate, pick a random one."
            "Do not include anything else in your reply."
        )
        color_prompt = f"Convert the following: {content}"
        cls.reprompt_conversation(system_name, system_prompt)
        cls.add_message(system_name, "niddelicious", color_prompt)
        response = await cls.request_chat(cls.get_conversation(system_name), chaos=0)
        reply = response["choices"][0]["message"]["content"]
        SessionData.add_tokens(tokens=int(response["usage"]["total_tokens"]))

        colors = Utilities.extract_colors(reply)
        return colors

    @classmethod
    async def command_intepretor(cls, content: str = None, author: str = None):
        if cls.get_status() != ModuleStatus.RUNNING:
            return None

        system_name = "ai_command_generator"
        system_prompt = (
            "You are a Twitch Command Message Generator named botdelicious."
            "You are working for niddelicious, a DJ streamer."
            "Your job is to reply to !commands from users in chat."
            "You will create excited and engaging messages appropriate for"
            "the !command that is provided to you."
            "Keep messages sassy and below 490 characters."
        )
        cls.reprompt_conversation(system_name, system_prompt)
        command_prompt = f"@{author}: {content}"
        cls.add_message(system_name, author, command_prompt)
        response = await cls.request_chat(cls.get_conversation(system_name))
        reply = response["choices"][0]["message"]["content"]
        SessionData.add_tokens(tokens=int(response["usage"]["total_tokens"]))

        reply = Utilities.clean_ai_replies(reply)
        return reply

    @classmethod
    async def event_intepretor(cls, content: str = None):
        if cls.get_status() != ModuleStatus.RUNNING:
            return None

        system_name = "ai_event_generator"
        system_prompt = (
            "You are a Twitch Event Message Generator"
            "in the chat of niddelicious, a DJ streamer."
            "You will create extensive, elaborate and hyped messages"
            "appropriate for the event that is provided to you."
            "Keep messages sassy and below 490 characters."
        )
        cls.reprompt_conversation(system_name, system_prompt)
        event_prompt = f"{content}"
        cls.add_message(system_name, "Twitch", event_prompt)
        response = await cls.request_chat(cls.get_conversation(system_name))
        reply = response["choices"][0]["message"]["content"]
        SessionData.add_tokens(tokens=int(response["usage"]["total_tokens"]))
        reply = Utilities.clean_ai_replies(reply)
        return reply

    @classmethod
    async def pa_intepretor(cls, content: str = None, author: str = None):
        if cls.get_status() != ModuleStatus.RUNNING:
            return None

        system_name = "ai_pa_generator"
        system_prompt = (
            "You are a Twitch Public Announcement Message Generator named botdelicious."
            "You are working for niddelicious, a DJ streamer."
            "Your job is to write announcements"
            "You will create engaging messages appropriate for"
            "the announcement that is provided to you."
            "Keep messages sassy and below 490 characters."
            "Do not use breaklines in your reply."
        )
        cls.reprompt_conversation(system_name, system_prompt)
        command_prompt = f"@{author}: {content}"
        cls.add_message(system_name, author, command_prompt)
        response = await cls.request_chat(cls.get_conversation(system_name))
        reply = response["choices"][0]["message"]["content"]
        SessionData.add_tokens(tokens=int(response["usage"]["total_tokens"]))

        reply = Utilities.clean_ai_replies(reply)
        return reply
