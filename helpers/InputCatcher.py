import logging


class InputCatcher:
    def __init__(self, parent):
        self.parent = parent
        self.modulesManager = parent.modulesManager

    def commandline(self):
        command = input("Command: \n")
        if command == "exit":
            self.modulesManager.stopWebhook()
            self.modulesManager.stopTwitch()
            self.modulesManager.stopObs()
            logging.info(f"Exiting...\n")
            return 0
        if command == "start twitch":
            self.modulesManager.startModule(moduleName="twitch", eventLoop=True)
        if command == "stop twitch":
            self.modulesManager.startTwitch()
        if command == "start event":
            self.modulesManager.startModule(moduleName="event", eventLoop=True)
        if command == "stop event":
            self.modulesManager.stopEvent()
        if command == "start webhook":
            self.modulesManager.startModule(moduleName="webhook")
        if command == "stop webhook":
            self.modulesManager.stopWebhook()
        if command == "start djctl":
            self.modulesManager.startModule(moduleName="djctl")
        if command == "stop djctl":
            self.modulesManager.stopDjctl()
        if command == "start obs":
            self.modulesManager.startModule(moduleName="obs", eventLoop=True)
        if command == "stop obs":
            self.modulesManager.stopObs()
        if command == "start podcast":
            self.modulesManager.startModule(moduleName="podcast", eventLoop=True)
        if command == "stop podcast":
            self.modulesManager.stopPodcast()
        if command == "status":
            self.parent.threadsStatus()
        if command == "check":
            self.parent.modules.event.module.checkLoopIsRunning()
        if command == "loop":
            self.parent.eventLoopManager.start()
        else:
            self.command = command
        return 1
