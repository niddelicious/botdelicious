import logging
from AsyncioThread import AsyncioThread
from Modules.ChatModule import ChatModule
from Modules.EventModule import EventModule
from Modules.OBSModule import OBSModule
from Modules.OpenaiModule import OpenaiModule
from Modules.WebhookModule import WebhookModule
from Modules.DJctlModule import DJctlModule
from Modules.TwinklyModule import TwinklyModule
from Modules.StableDiffusionModule import StableDiffusionModule
from Helpers.Enums import ModuleStatus


class ModulesController:
    _modules = {
        "event": EventModule(),
        "webhook": WebhookModule(),
        "twitch": OBSModule("twitch"),
        "podcast": OBSModule("podcast"),
        "video": OBSModule("video"),
        "chat": ChatModule(),
        "djctl": DJctlModule(),
        "twinkly": TwinklyModule(),
        "openai": OpenaiModule(),
        "stablediffusion": StableDiffusionModule(),
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
        AsyncioThread.run_coroutine(module.stop())
        if module.status() is ModuleStatus.RUNNING:
            logging.debug(f"Stopping module: {module_name}")
            AsyncioThread.run_coroutine(module.stop())

    @classmethod
    def get_module(cls, module_name):
        return cls._modules.get(module_name) or None

    @classmethod
    def get_module_status(cls, module_name=None):
        logging.info(f"Module status:")
        if module_name:
            module = cls.get_module(module_name)
            status = module.get_status()
            logging.info(f"Module: {module_name} - Status: {status}")
            return status
        for name, module in cls._modules.items():
            logging.info(f"Module: {name} - Status: {module.get_status()}")

    @classmethod
    def list_modules(cls):
        return cls._modules.keys()
