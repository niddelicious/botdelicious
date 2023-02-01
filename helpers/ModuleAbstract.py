from abc import ABC, abstractmethod
from helpers.Enums import ModuleStatus


class BotdeliciousModule(ABC):
    def __init__(self, messageHandler=None):
        self.status = ModuleStatus.IDLE
        self.messageHandler = messageHandler

    @abstractmethod
    def start(self):
        """Start the module"""
        self.status = ModuleStatus.RUNNING

    @abstractmethod
    def stop(self):
        """Stop the module"""
        self.status = ModuleStatus.STOPPING
        self.status = ModuleStatus.IDLE

    @abstractmethod
    def status(self):
        """Return the status of the module"""
        return self.status
