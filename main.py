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
from modules.OBS import OBS

from enums import ThreadState


class Botdelicious:
    def __init__(self):
        self._config = None
        self.state = ThreadState.IDLE
        self.threads = DotMap({})
        self.getConfig()
        self.autostart()

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, configuration):
        self._config = configuration

    def autostart(self):
        with open("autostart.yml", "r") as autostart:
            autostarts = DotMap(yaml.load(autostart, Loader=yaml.FullLoader))
        for module in autostarts.modules:
            self.startModule(moduleName=module.name, eventLoop=module.loop)

    def inputListener(self):
        command = input("Command: \n")
        if command == "exit":
            if hasattr(self, "webhook"):
                self.webhook.stop()
            logging.info(f"Exiting...\n")
            return 0
        if command == "start twitch":
            self.startModule(moduleName="twitch", eventLoop=True)
        if command == "start webhook":
            self.startModule(moduleName="webhook")
        if command == "start obs":
            self.startModule(moduleName="obs", eventLoop=True)
        if command == "status":
            self.threadsStatus()
        else:
            self.command = command
        return 1

    def threadsStatus(self):
        logging.info(self.threads)

    def startModule(self, moduleName=None, eventLoop=None):
        threadName = moduleName.capitalize()
        moduleStartFunctionName = f"start{moduleName.capitalize()}"
        moduleStartFunction = getattr(self, moduleStartFunctionName)
        eventLoop = asyncio.new_event_loop() if eventLoop is True else None
        self.threads[moduleName] = Thread(
            target=moduleStartFunction, name=threadName, args=(eventLoop,), daemon=True
        )
        self.threads[moduleName].start()
        if eventLoop:
            eventLoop.stop()

    def startWebhook(self, *args, **kwargs):
        self.webhook = Webhook(self.config.webhook.port)

    def startObs(self, eventLoop: asyncio.AbstractEventLoop, *args, **kwargs):
        asyncio.set_event_loop(eventLoop)
        eventLoop.run_forever()
        self.obs = OBS(self.config.obs.port, self.config.obs.password)
        eventLoop.run_until_complete(self.obs.connect())

    def startTwitch(self, eventLoop: asyncio.AbstractEventLoop, *args, **kwargs):
        asyncio.set_event_loop(eventLoop)
        eventLoop.run_forever()
        self.twitch = TwitchChat(Bot=self)
        self.twitch.run()

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
