"""
A Twitch chat-bot, with integrations towards Twitch, OBS, Engine OS/SoundStage, Ko-fi, and Twinkly
"""

__author__ = "Nidde Nedelius"
__license__ = "MIT"
__version__ = "0.1.0"

import sys
from threading import Thread
import asyncio
import time
import yaml
from dotmap import DotMap
import logging
import coloredlogs
from queue import Queue

from helpers.Enums import ThreadState, ModuleStatus
from helpers.EventHandler import EventHandler
from helpers.EventLoopManager import EventLoopManager
from helpers.InputCatcher import InputCatcher
from helpers.ModuleManager import ModuleManager
from helpers.ConfigManager import ConfigManager


class Botdelicious:
    def __init__(self):
        self._config = None
        self.state = ThreadState.IDLE
        self.threads = DotMap({})
        self.modules = DotMap({})
        self.queue = Queue()
        self.eventLoopManager = EventLoopManager(queue=self.queue)
        self.eventHandler = EventHandler()
        self.configManager = ConfigManager(parent=self)
        self.configManager.getConfig()
        self.threads["eventLoopManager"] = Thread(
            target=self.eventLoopManager, args=(self.queue,)
        )
        self.threads["eventLoopManager"].start()
        self.modulesManager = ModuleManager(parent=self)
        self.inputCatcher = InputCatcher(parent=self)

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
            self.modulesManager.startModule(
                moduleName=module.name, eventLoop=module.loop
            )

    def threadsStatus(self):
        logging.info(self.threads)


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

    """Main entry point of the app"""
    b.autostart()
    while not b.queue.empty():
        logging.debug(f"Queue: {b.queue}")
        logging.debug(f"LoopManager: {b.eventLoopManager}")
        logging.debug(f"Threads: {b.threads}")
        logging.debug(f"Thread: {b.threads.eventLoopManager}")
        time.sleep(3)
    while b.inputCatcher.commandline():
        pass
    logger.info(f"Application ended\n")


if __name__ == "__main__":
    """This is executed when run from the command line"""
    main()
