import logging


class InputCatcher:
    def __init__(self, parent):
        self.parent = parent
        self.moduleManager = parent.modulesManager

    def commandline(self):
        command = input("Command: \n")
        if command == "exit":
            self.moduleManager.stopWebhook()
            self.moduleManager.stopTwitch()
            self.moduleManager.stopObs()
            logging.info(f"Exiting...\n")
            return 0
        if command == "start twitch":
            self.moduleManager.startModule(moduleName="twitch", eventLoop=True)
        if command == "stop twitch":
            self.moduleManager.startTwitch()
        if command == "start webhook":
            self.moduleManager.startModule(moduleName="webhook")
        if command == "stop webhook":
            self.moduleManager.stopWebhook()
        if command == "start djctl":
            self.moduleManager.startModule(moduleName="djctl")
        if command == "stop djctl":
            self.moduleManager.stopDjctl()
        if command == "start obs":
            self.moduleManager.startModule(moduleName="obs", eventLoop=True)
        if command == "stop obs":
            self.moduleManager.stopObs()
        if command == "start podcast":
            self.moduleManager.startModule(moduleName="podcast", eventLoop=True)
        if command == "stop podcast":
            self.moduleManager.stopPodcast()
        if command == "status":
            self.bot.threadsStatus()
        if command == "check":
            self.bot.eventLoopManager.checkLoopIsRunning()
        if command == "loop":
            self.bot.eventLoopManager.start()
        else:
            self.command = command
        return 1
