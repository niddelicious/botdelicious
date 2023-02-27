"""
A Twitch chat-bot, with integrations towards Twitch, OBS,
Engine OS/SoundStage, Ko-fi, and Twinkly
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
        ConfigManager.get_config()
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
    logger = logging.getLogger()
    logger.setLevel(ConfigManager.config.logging.level)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", "%m-%d-%Y %H:%M:%S"
    )
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    coloredlogs.install(
        level=ConfigManager.config.logging.level, logger=logger
    )

    """Main entry point of the app"""
    AsyncioThread.start_loop()
    b.autostart()
    while b.inputCatcher.commandline():
        pass
    AsyncioThread.stop_loop()
    logger.info(f"Application ended\n")


if __name__ == "__main__":
    """This is executed when run from the command line"""
    main()
