import logging
import simpleobsws
from abc import ABC, abstractmethod
from Helpers.Enums import OBSConnectionStatus


class OBSInstance(ABC):
    _status = OBSConnectionStatus.DISCONNECTED

    def __init__(self):
        self.set_status(OBSConnectionStatus.DISCONNECTED)

    @classmethod
    def get_status(cls):
        return cls._status

    @classmethod
    def set_status(cls, new_status: OBSConnectionStatus):
        cls._status = new_status

    @classmethod
    def status(self):
        """Return the status of the module"""
        return self.get_status()

    @classmethod
    async def _call(
        cls,
        type: str = "Call",
        request: simpleobsws.Request = None,
        *args,
        **kwargs,
    ):
        ret = await cls.ws.call(request)  # Perform the request

        if ret.ok():  # Check if the request succeeded
            logging.debug(f"|{cls._name}| {type} succeeded!")
            logging.debug(f"Response data: {ret.responseData}")
            return ret.responseData
        else:
            logging.warn(f"|{cls._name}| {type} failed!")
            logging.warn(f"Response data: {ret.responseData}")
            return ret.responseData
