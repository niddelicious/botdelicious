"""
A Twitch chat-bot, with integrations towards Twitch, OBS,
Engine OS/SoundStage, Ko-fi, and Twinkly
"""

__author__ = "Nidde Nedelius"
__license__ = "MIT"
__version__ = "0.1.0"

import sys
import yaml
import datetime
from dotmap import DotMap
import logging
import coloredlogs

from AsyncioThread import AsyncioThread
from Helpers.CommandLine import CommandLine

from Controllers.ModulesController import ModulesController
from Controllers.ConfigController import ConfigController
from Helpers.SessionData import SessionData
from Modules.EventModule import EventModule


class Botdelicious:
    def autostart(self):
        with open("autostart.yml", "r") as autostart:
            autostarts = DotMap(yaml.load(autostart, Loader=yaml.FullLoader))
        for module in autostarts.modules:
            ModulesController.start_module(module_name=module.name)


def main():
    ConfigController.get_config()
    if ConfigController._config["logging"]["log_to_file"]:
        log_filename = datetime.datetime.now().strftime(
            "logs/debug-%Y-%m-%d_%H-%M-%S.log"
        )

        logging.basicConfig(
            filename=log_filename,
            filemode="a",  # Append to the log file
            format="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%m-%d-%Y %H:%M:%S",
            level=logging.DEBUG,  # Set to DEBUG level for the file handler
        )

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set logger to DEBUG to capture all levels

    # Console (stdout) handler for INFO and higher
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Set to INFO level for console
    log_format = "%(asctime)s | %(levelname)s | %(message)s"
    date_format = "%m-%d-%Y %H:%M:%S"
    formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    coloredlogs.install(
        level=ConfigController._config.logging.level,
        logger=logger,
        fmt=log_format,
        datefmt=date_format,
    )

    """Main entry point of the app"""
    b = Botdelicious()
    b.autostart()
    sleep_time = 2 if logging.getLogger().getEffectiveLevel() == logging.DEBUG else 0
    EventModule.set_loop_sleep(sleep_time=sleep_time)
    SessionData.start_session()
    while CommandLine.cli():
        pass
    AsyncioThread.stop_loop()
    logger.info(f"Application ended\n")


if __name__ == "__main__":
    """This is executed when run from the command line"""
    main()
