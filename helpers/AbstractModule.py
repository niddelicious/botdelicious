from abc import ABC, abstractmethod
from helpers.Enums import ModuleStatus


class BotdeliciousModule(ABC):
    _status = ModuleStatus.IDLE

    def __init__(self):
        self._status = ModuleStatus.IDLE

    @abstractmethod
    async def start(self):
        """Start the module"""
        self._status = ModuleStatus.RUNNING

    @abstractmethod
    async def stop(self):
        """Stop the module"""
        self._status = ModuleStatus.STOPPING
        self._status = ModuleStatus.IDLE

    @abstractmethod
    async def _status(self):
        """Return the status of the module"""
        return self._status
