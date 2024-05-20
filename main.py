"""
A Twitch chat-bot, with integrations towards Twitch, OBS,
Engine OS/SoundStage, Ko-fi, and Twinkly
"""

__author__ = "Nidde Nedelius"
__license__ = "MIT"
__version__ = "0.1.0"

import os

try:
    import curses
except ImportError:
    import _curses as curses
from pathlib import Path
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
from Helpers.TwitchUpdateTool import TwitchUpdateTool
from Helpers.OBSInfoTool import OBSInfoTool
from Modules.EventModule import EventModule


class Botdelicious:
    def set_profile_path(self, path):
        self._config_base_path = Path(path)

    def _get_path(self, filename="autostart.yml"):
        return self._config_base_path / filename

    def autostart(self):
        profile_path = self._get_path()
        with open(profile_path, "r") as autostart:
            autostarts = DotMap(yaml.load(autostart, Loader=yaml.FullLoader))
        for module in autostarts.modules:
            ModulesController.start_module(module_name=module.name)


def list_subfolders(directory):
    """List all subdirectories in the given directory"""
    return [
        name
        for name in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, name))
    ]


def menu(options):
    """Display a simple selection menu with basic highlighting"""
    if not options:
        print("No subfolders found.")
        return None

    selection = -1
    while True:
        os.system("cls" if os.name == "nt" else "clear")  # Clear the console window

        for index, option in enumerate(options):
            if index == selection:
                # Highlight selected option
                print(
                    f"\033[1;32m{index + 1}. {option}\033[0m"
                )  # Bright Green and bold text
            else:
                print(f"{index + 1}. {option}")

        try:
            selection = int(input("Select a Profile: ")) - 1
            if 0 <= selection < len(options):
                return f"./Profiles/{options[selection]}"
            else:
                print("Invalid selection. Please choose a valid number.")
                selection = -1  # Reset invalid selection
        except ValueError:
            print("Please enter a number.")
            selection = -1  # Reset on error


def setup_logging(base_path):
    log_directory = Path(base_path) / "logs"
    log_directory.mkdir(exist_ok=True)
    log_filename = log_directory / datetime.datetime.now().strftime(
        "debug-%Y-%m-%d_%H-%M-%S.log"
    )
    print(f"Logging to: {str(log_filename)}")  # Confirm the log file path

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Root logger catches everything at DEBUG level

    # Clear existing handlers if any to avoid duplicates when re-running the setup
    if logger.hasHandlers():
        logger.handlers.clear()

    # File Handler - catches all DEBUG and higher level messages
    file_handler = logging.FileHandler(str(log_filename), encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", "%m-%d-%Y %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Colored logs setup for console, only showing INFO and higher
    coloredlogs.install(
        level=ConfigController.get("logging").level,
        logger=logger,
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%m-%d-%Y %H:%M:%S",
    )

    return logger  # Optionally return the logger


def main():
    directory = "./Profiles"
    subdirs = list_subfolders(directory)

    profile_dir = menu(subdirs)
    if profile_dir:
        print(f"Selected Profile: {profile_dir}")
        # You can now use `selected_folder` for further operations, such as setting up config files.

    ConfigController.set_config_base_path(profile_dir)
    ConfigController.get_config()

    setup_logging(profile_dir)

    # Create logger
    logger = logging.getLogger()
    logger.info(f"Application started")

    """Main entry point of the app"""
    b = Botdelicious()
    b.set_profile_path(profile_dir)
    twitch_update_tool = TwitchUpdateTool()
    twitch_update_tool.refresh_tokens()
    twitch_config = ConfigController.get_config_file("twitch_channel.yaml")
    new_twitch_title = twitch_update_tool.title_assembler(
        twitch_config.info.series,
        twitch_config.info.episode,
        twitch_config.info.genre,
        twitch_config.info.tagline,
    )
    new_tags = twitch_config.info.tags
    new_tags = twitch_update_tool.genre_to_tags(twitch_config.info.genre, new_tags)
    if twitch_update_tool.update_twitch_channel(
        title=new_twitch_title,
        category_id=twitch_config.info.category_id,
        tags=new_tags,
    ):
        logger.info(f"Updated Twitch channel with new title: {new_twitch_title}")
    else:
        logger.error(
            f"Failed to update Twitch channel with new title: {new_twitch_title}"
        )
    obs_info_tool = OBSInfoTool()
    obs_info_tool.update_show_info(profile_dir)
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
