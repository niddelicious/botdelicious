"""
A Twitch chat-bot, with integrations towards Twitch, OBS, Engine OS/SoundStage, Ko-fi, and Twinkly
"""

__author__ = "Nidde Nedelius"
__license__ = "MIT"
__version__ = "0.1.0"

import sys
from threading import Thread
import yaml
from dotmap import DotMap
import logging
import coloredlogs


class Botdelicious:
    def __init__(self):
        with open("config.yml", "r") as config:
            self.config = DotMap(yaml.load(config, Loader=yaml.FullLoader))
        self.command = False
        self.newCommand = False
        self.stop = False
        self.running = False

    def start(self):
        self.startThread()
        logging.info(f"Listening for commands...\n")

    def looper(self, *args, **kwargs):
        logging.info(f"Starting loop...\n")
        self.running = True
        while self.running:
            if self.stop:
                self.running = False
            if self.command:
                self.newCommand = self.command
                self.command = False
                self.runCommand(self.newCommand)
                self.newCommand = False
        logging.info(f"Loop completed\n")
        delattr(self, "t")
        self.running = False
        return

    def startThread(self):
        logging.info(f"Starting thread...\n")
        if hasattr(self, "t"):
            if self.t.is_alive():
                print(f"Thread already running...\n")
                return
        else:
            self.initThread()
        self.t.start()

    def initThread(self):
        logging.info(f"Initializing thread...\n")
        self.t = Thread(target=self.looper, args=())

    def stopThread(self):
        logging.info(f"Stopping thread...\n")
        while self.running:
            self.stop = True
        if hasattr(self, "t"):
            self.t.join()
        self.stop = False

    def restartLooper(self):
        logging.info(f"Restarting loop...\n")
        self.stopThread()
        self.startThread()

    def runCommand(self, cmd):
        logging.info(f"Running command: {cmd}\n")

    def inputListener(self):
        command = input("Command: \n")
        if command == "exit":
            self.stopThread()
            logging.info(f"Exiting...\n")
            return 0
        elif command == "restart":
            self.restartLooper()
        else:
            self.command = command

        return 1


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

    b.start()
    """Main entry point of the app"""
    while b.inputListener():
        pass
    print(f"Application ended\n")


if __name__ == "__main__":
    """This is executed when run from the command line"""
    main()
