import logging
import openai
from openai import OpenAIError
from helpers.SessionData import SessionData

from helpers.AbstractModule import BotdeliciousModule
from helpers.Dataclasses import ConversationEntry
from helpers.Enums import ConversationStatus, ModuleStatus

DEFAULT_SYSTEM_MESSAGE = "You are a positive and just a little bit sassy chatbot named botdelicious occupying the live chat channel for niddelicious, who is a DJ streamer on Twitch. You are not an assistant, nor an AI language model, you're just another channel moderator hanging out and having fun. You are currently having a conversation with a viewer named {username}. Keep replies shorter than 500 characters."
DEFAULT_THINKING_MESSAGE = (
    "@{username} I'm still thinking about your last message 🤔"
)
DEFAULT_ERROR_MESSAGE = (
    "Sorry, I'm a bit distracted right now. Try again later."
)


class OpenaiModule(BotdeliciousModule):
    _conversations = {}
    _conversation_status = {}

    def __init__(self, config) -> None:
        openai.organization = config.org
        openai.api_key = config.key

    async def start(self):
        self.set_status(ModuleStatus.RUNNING)

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        self.set_status(ModuleStatus.IDLE)

    @classmethod
    def start_conversation(cls, username):
        cls._conversations[username] = [
            ConversationEntry(
                "system", DEFAULT_SYSTEM_MESSAGE.format(username=username)
            )
        ]
        cls._conversation_status[username] = ConversationStatus.IDLE

    @classmethod
    def add_message(cls, username, message):
        cls._conversations[username].append(ConversationEntry("user", message))
        if len(cls._conversations[username]) > 9:
            del cls._conversations[username][1:3]

    @classmethod
    def add_reply(cls, username, reply):
        cls._conversations[username].append(
            ConversationEntry("assistant", reply)
        )

    @classmethod
    def get_conversation(cls, username):
        logging.debug(cls._conversations[username])
        return cls._conversations[username]

    @classmethod
    def get_conversation_status(cls, username):
        if username not in cls._conversation_status:
            cls.start_conversation(username)
        logging.debug(
            f"Conversation status for {username} is {cls._conversation_status[username]}"
        )
        return cls._conversation_status[username]

    @classmethod
    def set_conversation_status(cls, username, status):
        cls._conversation_status[username] = status

    async def request(self, messages):
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

    async def chat(self, username: str = None, message: str = None):
        if self.get_status() != ModuleStatus.RUNNING:
            return False
        if self.get_conversation_status(username) == ConversationStatus.IDLE:
            self.set_conversation_status(username, ConversationStatus.OCCUPIED)
            self.add_message(username, message)
            response = await self.request(self.get_conversation(username))
            if response:
                SessionData.add_tokens(
                    tokens=int(response["usage"]["total_tokens"])
                )
                reply = response["choices"][0]["message"]["content"]
                self.add_reply(username, reply)
            else:
                reply = DEFAULT_ERROR_MESSAGE
            self.set_conversation_status(username, ConversationStatus.IDLE)
        else:
            reply = DEFAULT_THINKING_MESSAGE.format(username=username)
        return reply
