"""
A Twitch chat-bot, with integrations towards Twitch, OBS, Engine OS/SoundStage, Ko-fi, and Twinkly
"""

__author__ = "Nidde Nedelius"
__license__ = "MIT"
__version__ = "0.1.0"

import sys
import yaml
from dotmap import DotMap
import logging
import coloredlogs

from AsyncioThread import AsyncioThread
from helpers.Enums import ThreadState

from helpers.InputCatcher import InputCatcher
from helpers.ModulesManager import ModulesManager
from helpers.ConfigManager import ConfigManager


class Botdelicious:
    eventHandler = None

    def __init__(self):
        self._config = None
        self.state = ThreadState.IDLE
        self.modules = DotMap({})
        self.configManager = ConfigManager(parent=self)
        self.configManager.getConfig()
        self.modulesManager = ModulesManager(parent=self)
        self.inputCatcher = InputCatcher(parent=self)

    @classmethod
    def getEventHandler(cls):
        logging.debug(f"Fetching EventHandler:{cls.eventHandler}")
        return cls.eventHandler

    @classmethod
    def setEventHandler(cls, eventHandler):
        logging.debug(f"EventHandler before:{cls.eventHandler}")
        cls.eventHandler = eventHandler
        logging.debug(f"EventHandler after:{cls.eventHandler}")

    def start_asyncio_thread(self):
        self._asyncio_thread = AsyncioThread()
        self._asyncio_thread.start_loop()

    def stop_asyncio_thread(self):
        if self._asyncio_thread is not None:
            self._asyncio_thread.stop_loop()
            self._asyncio_thread = None

    def run_asyncio_coroutine(self, coro):
        if self._asyncio_thread is None:
            self.start_asyncio_thread()
        self._asyncio_thread.run_coroutine(coro)

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
            self.modulesManager.startModule(moduleName=module.name)

def main():
    b = Botdelicious()
    b.start_asyncio_thread()
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
    while b.inputCatcher.commandline():
        pass
    b.stop_asyncio_thread()
    logger.info(f"Application ended\n")


if __name__ == "__main__":
    """This is executed when run from the command line"""
    main()
