import logging
from AsyncioThread import AsyncioThread
from modules.Chat import ChatModule
from modules.Event import EventModule
from modules.OBS import OBSModule
from modules.Webhook import WebhookModule
from modules.DJctl import DJctlModule
from modules.Twinkly import TwinklyModule
from helpers.Enums import ModuleStatus


class ModulesManager:
    _modules = {
        "event": EventModule(),
        "webhook": WebhookModule(),
        "twitch": OBSModule("twitch"),
        "podcast": OBSModule("podcast"),
        "video": OBSModule("video"),
        "chat": ChatModule(),
        "djctl": DJctlModule(),
        "twinkly": TwinklyModule(),
    }

    @classmethod
    def start_module(cls, module_name=None):
        module = cls.get_module(module_name)
        if module.status() is ModuleStatus.IDLE:
            logging.debug(f"Starting module: {module_name}")
            AsyncioThread.run_coroutine(module.start())

    @classmethod
    def stop_module(cls, module_name=None):
        module = cls.get_module(module_name)
        if module.status() is ModuleStatus.RUNNING:
            logging.debug(f"Stopping module: {module_name}")
            AsyncioThread.run_coroutine(module.stop())

    @classmethod
    def get_module(cls, module_name):
        return cls._modules.get(module_name) or None

    @classmethod
    def get_module_status(cls):
        logging.info(f"Module status:")
        for name, module in cls._modules.items():
            logging.info(name)
            logging.info(module.get_status())
