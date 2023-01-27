"""
A Twitch chat-bot, with integrations towards Twitch, OBS, Engine OS/SoundStage, Ko-fi, and Twinkly
"""

__author__ = "Nidde Nedelius"
__license__ = "MIT"
__version__ = "0.1.0"

import sys
from threading import Thread
import asyncio
import yaml
from dotmap import DotMap
import logging
import coloredlogs

from modules.TwitchChat import TwitchChat
from modules.Webhook import Webhook

from enums import ThreadState


class Botdelicious:
    def __init__(self):
        self._config = None
        self.state = ThreadState.IDLE
        self.threads = DotMap({})
        self.getConfig()

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, configuration):
        self._config = configuration

    def inputListener(self):
        command = input("Command: \n")
        if command == "exit":
            if hasattr(self, "webhook"):
                self.webhook.stop()
            logging.info(f"Exiting...\n")
            return 0
        if command == "twitch":
            loop = asyncio.new_event_loop()
            self.threads.twitch = Thread(
                target=self.startTwitch, name="TwitchChat", args=(loop,), daemon=True
            )
            self.threads.twitch.start()
            loop.stop()
        if command == "webhook":
            self.threads.webhook = Thread(
                target=self.startWebhook, name="Webhook", args=(), daemon=True
            )
            self.threads.webhook.start()
        if command == "status":
            self.threadsStatus()
        else:
            self.command = command
        return 1

    def threadsStatus(self):
        logging.info(self.threads)

    def startWebhook(self):
        self.webhook = Webhook(self.config.webhook.port)

    def startTwitch(self, eventLoop: asyncio.AbstractEventLoop):
        logging.info(eventLoop)
        logging.info("Starting TwitchChat")
        asyncio.set_event_loop(eventLoop)
        eventLoop.run_forever()
        logging.info("Loading TwitchChat")
        self.twitch = TwitchChat(Bot=self)
        logging.info("Running TwitchChat")
        self.twitch.run()
        logging.info("TwitchChat currently running...")

    def updateConfig(self, group, setting, value):
        with open("config.yml") as configFile:
            config = yaml.load(configFile, Loader=yaml.FullLoader)

        config[group][setting] = value

        with open("config.yml", "w") as configFile:
            yaml.dump(config, configFile)
        self.getConfig()

    def getConfig(self):
        with open("config.yml", "r") as config:
            self.config = DotMap(yaml.load(config, Loader=yaml.FullLoader))


def main():
    b = Botdelicious()
    logger = logging.getLogger()
    logger.setLevel(b.config.logging.level)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", "%m-%d-%Y %H:%M:%S"
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    coloredlogs.install(level=b.config.logging.level, logger=logger)

    # b.start()
    """Main entry point of the app"""
    while b.inputListener():
        pass
    logger.info(f"Application ended\n")


if __name__ == "__main__":
    """This is executed when run from the command line"""
    main()
