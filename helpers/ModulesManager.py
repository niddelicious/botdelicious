import logging
from AsyncioThread import AsyncioThread
from modules.Chat import ChatModule
from modules.Event import EventModule
from modules.OBS import OBSModule
from modules.Webhook import WebhookModule


class ModulesManager:
    _modules = {
        "event": EventModule(),
        "webhook": WebhookModule(),
        "twitch": OBSModule("twitch"),
        "podcast": OBSModule("podcast"),
        # "chat": ChatModule(),
    }

    @classmethod
    def start_module(cls, module_name=None):
        logging.debug(f"Starting module: {module_name}")
        module = cls._modules[module_name]
        AsyncioThread.run_coroutine(module.start())

    @classmethod
    def stop_module(cls, module_name=None):
        logging.debug(f"Stopping module: {module_name}")
        module = getattr(cls._modules, module_name)
        AsyncioThread.run_coroutine(module.stop())

    @classmethod
    def get_module(cls, module_name):
        return cls._modules[module_name] or None
