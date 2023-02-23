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
from modules.DJctl import DJctl

from helpers.Enums import ThreadState, ModuleStatus
from helpers.EventHandler import EventHandler
from helpers.EventLoopManager import EventLoopManager


class Botdelicious:
    def __init__(self):
        self._config = None
        self.state = ThreadState.IDLE
        self.threads = DotMap({})
        self.modules = DotMap({})
        self.eventLoop = EventLoopManager()
        self.eventLoop.start()
        self.eventHandlerLoop = asyncio.new_event_loop()
        self.eventHandler = EventHandler(
            modules=self.modules, loop=self.eventHandlerLoop
        )
        self.getConfig()
        self.threads["eventHandler"] = Thread(
            target=self.startEventHandler,
            name="EventHandler",
            args=(self.eventHandlerLoop,),
            daemon=True,
        )

    def startEventHandler(self, eventHandler: EventHandler, eventHandlerLoop):
        asyncio.set_event_loop(eventHandlerLoop)
        eventHandlerLoop.run_forever()
        self.eventHandler = eventHandler
        self.eventHandler.start()

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
            self.stopWebhook()
            self.stopTwitch()
            self.stopObs()
            logging.info(f"Exiting...\n")
            return 0
        if command == "start twitch":
            self.startModule(moduleName="twitch", eventLoop=True)
        if command == "stop twitch":
            self.startTwitch()
        if command == "start webhook":
            self.startModule(moduleName="webhook")
        if command == "stop webhook":
            self.stopWebhook()
        if command == "start djctl":
            self.startModule(moduleName="djctl")
        if command == "stop djctl":
            self.stopDjctl()
        if command == "start obs":
            self.startModule(moduleName="obs", eventLoop=True)
        if command == "stop obs":
            self.stopObs()
        if command == "start podcast":
            self.startModule(moduleName="podcast", eventLoop=True)
        if command == "stop podcast":
            self.stopPodcast()
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
        self.modules.webhook.module = Webhook(
            self.config.webhook.port, eventHandler=self.eventHandler
        )

    def stopWebhook(self, *args, **kwargs):
        if self.modules.has_key("webhook"):
            self.modules.webhook.module.stop()

    def startDjctl(self, *args, **kwargs):
        self.modules.djctl.module = DJctl()
        self.modules.djctl.module.console()

    def stopDjctl(self, *args, **kwargs):
        if self.modules.has_key("djctl"):
            self.modules.djctl.module.stop()

    def startObs(self, eventLoop: asyncio.AbstractEventLoop, *args, **kwargs):
        self.modules.obs.loop = eventLoop
        asyncio.set_event_loop(self.modules.obs.loop)
        self.modules.obs.loop.run_forever()
        self.modules.obs.module = OBS(
            self.config.obs.port, self.config.obs.password, name="obs"
        )
        self.modules.obs.loop.run_until_complete(self.modules.obs.module.connect())

    def stopObs(self, *args, **kwargs):
        if self.modules.has_key("obs"):
            self.modules.obs.loop.run_until_complete(
                self.modules.obs.module.disconnect()
            )

    def startPodcast(self, eventLoop: asyncio.AbstractEventLoop, *args, **kwargs):
        self.modules.podcast.loop = eventLoop
        asyncio.set_event_loop(self.modules.podcast.loop)
        self.modules.podcast.loop.run_forever()
        self.modules.podcast.module = OBS(
            self.config.podcast.port, self.config.podcast.password, name="podcast"
        )
        self.modules.podcast.loop.run_until_complete(
            self.modules.podcast.module.connect()
        )

    def stopPodcast(self, *args, **kwargs):
        if self.modules.has_key("podcast"):
            self.modules.podcast.loop.run_until_complete(
                self.modules.podcast.module.disconnect()
            )
            self.modules.podcast.module.stop()

    def startTwitch(self, eventLoop: asyncio.AbstractEventLoop, *args, **kwargs):
        asyncio.set_event_loop(eventLoop)
        eventLoop.run_forever()
        self.modules.twitch.module = TwitchChat(Bot=self)
        self.modules.twitch.module.run()

    def stopTwitch(self, *args, **kwargs):
        if self.modules.has_key("twitch"):
            self.modules.twitch.loop.run_until_complete(
                self.modules.twitch.module.close()
            )
            self.modules.twitch.loop.stop()

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
    b.threads["eventHandler"].start()
    b.autostart()
    while b.inputListener():
        pass
    logger.info(f"Application ended\n")


if __name__ == "__main__":
    """This is executed when run from the command line"""
    main()
