import logging


class InputCatcher:
    def __init__(self, parent):
        self.parent = parent
        self.modulesManager = parent.modulesManager

    def commandline(self):
        command = input("Command: \n")
        if command == "exit":
            self.modulesManager.stopModule(moduleName="webhook")
            self.modulesManager.stopModule(moduleName="twitch")
            self.modulesManager.stopModule(moduleName="obs")
            self.modulesManager.stopModule(moduleName="podcast")
            logging.info(f"Exiting...\n")
            return 0
        if command == "start twitch":
            self.modulesManager.startModule(moduleName="twitch")
        if command == "stop twitch":
            self.modulesManager.stopModule(moduleName="twitch")
        if command == "start event":
            self.modulesManager.startModule(moduleName="event")
        if command == "stop event":
            logging.info(f"Cannot stop event loop. Exit application instead")
        if command == "start webhook":
            self.modulesManager.startModule(moduleName="webhook")
        if command == "stop webhook":
            self.modulesManager.stopModule(moduleName="webhook")
        if command == "start djctl":
            self.modulesManager.startModule(moduleName="djctl")
        if command == "stop djctl":
            self.modulesManager.stopModule(moduleName="djctl")
        if command == "start obs":
            self.modulesManager.startModule(moduleName="obs")
        if command == "stop obs":
            self.modulesManager.stopModule(moduleName="obs")
        if command == "start podcast":
            self.modulesManager.startModule(moduleName="podcast")
        if command == "stop podcast":
            self.modulesManager.stopModule(moduleName="podcast")
        if command == "loop":
            self.parent.eventLoopManager.start()
        else:
            self.command = command
        return 1
