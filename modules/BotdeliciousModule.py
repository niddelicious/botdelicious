from abc import ABC, abstractmethod
from Helpers.Enums import ModuleStatus


class BotdeliciousModule(ABC):
    _status = ModuleStatus.IDLE

    def __init__(self):
        self.set_status(ModuleStatus.IDLE)

    @classmethod
    def get_status(cls):
        return cls._status

    @classmethod
    def set_status(cls, new_status: ModuleStatus):
        cls._status = new_status

    @abstractmethod
    async def start(self):
        """Start the module"""
        self.set_status(ModuleStatus.RUNNING)

    @abstractmethod
    async def stop(self):
        """Stop the module"""
        self.set_status(ModuleStatus.STOPPING)
        self.set_status(ModuleStatus.IDLE)

    @classmethod
    def status(self):
        """Return the status of the module"""
        return self.get_status()
