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
from helpers.CommandLine import CommandLine

from helpers.ModulesManager import ModulesManager
from helpers.ConfigManager import ConfigManager
from helpers.SessionData import SessionData
from modules.Event import EventModule


class Botdelicious:
    def autostart(self):
        with open("autostart.yml", "r") as autostart:
            autostarts = DotMap(yaml.load(autostart, Loader=yaml.FullLoader))
        for module in autostarts.modules:
            ModulesManager.start_module(module_name=module.name)


def main():
    ConfigManager.get_config()
    logger = logging.getLogger()
    logger.setLevel(ConfigManager._config.logging.level)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", "%m-%d-%Y %H:%M:%S"
    )
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    coloredlogs.install(
        level=ConfigManager._config.logging.level, logger=logger
    )
    if ConfigManager._config.logging.log_to_file:
        logging.basicConfig(
            filename="debug.log", encoding="utf-8", level=logging.DEBUG
        )

    """Main entry point of the app"""
    b = Botdelicious()
    b.autostart()
    sleep_time = (
        2 if logging.getLogger().getEffectiveLevel() == logging.DEBUG else 0
    )
    EventModule.set_loop_sleep(sleep_time=sleep_time)
    SessionData.start_session()
    while CommandLine.cli():
        pass
    AsyncioThread.stop_loop()
    logger.info(f"Application ended\n")


if __name__ == "__main__":
    """This is executed when run from the command line"""
    main()
