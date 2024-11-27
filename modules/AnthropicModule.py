from pathlib import Path
import logging
import datetime
import anthropic
from Controllers.ConfigController import ConfigController
from Helpers.SessionData import SessionData

from Modules.BotdeliciousModule import BotdeliciousModule
from Helpers.Dataclasses import AnthropicEntry
from Helpers.Enums import ConversationStatus, ModuleStatus, QueueStatus
from Helpers.Utilities import Utilities


class AnthropicModule(BotdeliciousModule):
    _client = None
    _conversations = {}
    _conversation_status = {}
    _prompt = ""
    _thinking_message = ""
    _error_message = ""
    _model = ""
    _role = ""
    _name = ""
    _image_status: QueueStatus = QueueStatus.IDLE
    _logger = None
    _system_prompt = ""
    _event_prompt = ""
    _pa_prompt = ""
    _so_prompt = ""
    _cmd_prompt = ""

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def set_config(cls, config):
        cls._prompt = config.system_prompt
        cls._thinking_message = config.thinking_message
        cls._error_message = config.error_message
        cls._model = config.model
        cls._max_tokens = config.max_tokens
        cls._role = config.role
        cls._name = config.name
        cls._system_prompt = config.system_prompt
        cls._event_prompt = config.event_prompt
        cls._pa_prompt = config.pa_prompt
        cls._so_prompt = config.so_prompt
        cls._cmd_prompt = config.cmd_prompt

    async def start(self):
        config = ConfigController.get_config_file("anthropic.yaml")
        self.set_client(config.key)
        self.set_config(config)
        await self.anthropic_logging()
        self.set_status(ModuleStatus.RUNNING)

    @classmethod
    def set_client(cls, api_key):
        cls._client = anthropic.Anthropic(api_key=api_key)

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        self.set_status(ModuleStatus.IDLE)

    @classmethod
    async def anthropic_logging(cls):
        cls._logger = logging.getLogger(__name__)
        cls._logger.setLevel(logging.DEBUG)
        cls._logger.propagate = False
        profile_path = ConfigController._get_config_file_path("")

        log_directory = Path(profile_path) / "logs"
        log_directory.mkdir(exist_ok=True)
        log_filename = log_directory / datetime.datetime.now().strftime(
            f"{__name__}-%Y-%m-%d_%H-%M-%S.log"
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
        cls._conversations[conversation_group] = []
        cls._conversation_status[conversation_group] = ConversationStatus.IDLE

    @classmethod
    def reprompt_conversation(cls, conversation_group, prompt: str = None):
        cls.clean_conversation(conversation_group)
        conversation_prompt = (
            prompt if prompt else cls._prompt.format(username=conversation_group)
        )
        cls._conversations[conversation_group] = [
            AnthropicEntry("user", conversation_prompt)
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
        anthropic_message = f"> {username}: {message}"
        cls._conversations[conversation_group].append(
            AnthropicEntry(role, anthropic_message)
        )
        if len(cls._conversations[conversation_group]) > 100:
            del cls._conversations[conversation_group][1:3]

    @classmethod
    def add_reply(cls, conversation_group, reply):
        cls._conversations[conversation_group].append(AnthropicEntry(cls._role, reply))

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
    async def request_chat(cls, messages, assistant_message: str = None):
        try:
            cls._logger.info("New query:")
            json_messages = [
                {"role": message.role, "content": message.content}
                for message in messages
            ]
            if assistant_message:
                json_messages.append(
                    {
                        "role": assistant_message.role,
                        "content": assistant_message.content,
                    }
                )
            cls._logger.info(json_messages)
            response = cls._client.messages.create(
                max_tokens=cls._max_tokens,
                model=cls._model,
                system=cls._prompt,
                messages=json_messages,
            )
            if response:
                SessionData.add_tokens(
                    tokens=int(
                        (response.usage.input_tokens + response.usage.output_tokens)
                    )
                )
            logging.info(response)
            cls._logger.info(response)
            return response
        except Exception as e:
            logging.error(e)
            cls._logger.error(e)
            return None

    @classmethod
    async def chat(cls, channel: str = None, username: str = None, message: str = None):
        if cls.get_status() != ModuleStatus.RUNNING:
            return f"💤"
        if cls.get_conversation_status(channel) == ConversationStatus.IDLE:
            cls.set_conversation_status(channel, ConversationStatus.OCCUPIED)
            cls.add_message(channel, username, message)
            response = await cls.request_chat(
                cls.get_conversation(channel),
            )
            if response:
                try:
                    reply = response.content[0].text
                    cls.add_reply(channel, reply)
                except Exception as e:
                    logging.error(e)
                    cls._logger.error(e)
                    reply = cls._error_message.format(username=username)
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

        system_name = "user"
        system_prompt = cls._so_prompt

        username = Utilities.find_username(content)
        if username:
            user = await Utilities.get_twitch_user_info(username=username)
        else:
            user = None
            username = None
        if not user:
            system_prompt = "Hype Twitch Streamer Shoutout Generator"
            system_message = (
                f"Give a snarky reply about how @{author} "
                f"tried to shoutout @{username}, but that user doesn't exist."
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
            system_message = cls._so_prompt.format(
                username=username,
                live_message=live_message,
                game_name=game_name,
                title=title,
                user_description=user_description,
                tags=tags,
            )
            success = True

        # If using completion instead of chat
        # response = await self.request_chat(prompt=system_message)
        # reply = response["choices"][0]["text"]

        # If using chat instead of completion
        cls.reprompt_conversation(system_name, system_prompt)
        cls.add_message(system_name, "niddelicious", system_message)
        response = await cls.request_chat(cls.get_conversation(system_name))
        reply = response.content[0].text
        return success, username, reply, avatar_url

    @classmethod
    async def rgb_intepretor(cls, content: str = None, author: str = None):
        if cls.get_status() != ModuleStatus.RUNNING:
            return None

        system_name = "user"
        system_prompt = (
            "You are a RGB color converting bot, "
            " taking a description and translating it "
            "to a json format: "
            "{'red': value_red, 'green': value_green, 'blue': value_blue}. "
            "Do not answer in any other way. "
            "If no color is appropriate, pick a random one. "
            "Do not include anything else in your reply. "
        )
        color_prompt = f"Convert the following: {content}"
        cls.reprompt_conversation(system_name, system_prompt)
        cls.add_message(system_name, "niddelicious", color_prompt)
        response = await cls.request_chat(cls.get_conversation(system_name))
        reply = response.content[0].text

        colors = Utilities.extract_colors(reply)
        return colors

    @classmethod
    async def command_intepretor(cls, content: str = None, author: str = None):
        if cls.get_status() != ModuleStatus.RUNNING:
            return None

        system_name = "system"
        system_prompt = cls._cmd_prompt
        cls.reprompt_conversation(system_name, system_prompt)
        command_prompt = f"@{author}: {content}"
        cls.add_message(system_name, author, command_prompt)
        response = await cls.request_chat(cls.get_conversation(system_name))
        reply = response.content[0].text
        reply = Utilities.clean_ai_replies(reply)
        return reply

    @classmethod
    async def event_intepretor(cls, content: str = None):
        if cls.get_status() != ModuleStatus.RUNNING:
            return None

        system_name = "system"
        system_prompt = cls._event_prompt
        cls.reprompt_conversation(system_name, system_prompt)
        event_prompt = f"{content}"
        cls.add_message(system_name, "Twitch", event_prompt)
        response = await cls.request_chat(cls.get_conversation(system_name))
        reply = response.content[0].text
        reply = Utilities.clean_ai_replies(reply)
        return reply

    @classmethod
    async def pa_intepretor(cls, content: str = None, author: str = None):
        if cls.get_status() != ModuleStatus.RUNNING:
            return None

        system_name = "system"
        system_prompt = cls._pa_prompt
        cls.reprompt_conversation(system_name, system_prompt)
        command_prompt = f"@{author}: {content}"
        cls.add_message(system_name, author, command_prompt)
        response = await cls.request_chat(cls.get_conversation(system_name))
        reply = response.content[0].text
        reply = Utilities.clean_ai_replies(reply)
        return reply
