import logging
from AsyncioThread import AsyncioThread

from helpers.ModulesManager import ModulesManager
from modules.Event import EventModule


class InputCatcher:
    @classmethod
    def commandline(cls):
        command = input("Command: \n")
        if command == "exit":
            ModulesManager.stop_module(module_name="chat")
            ModulesManager.stop_module(module_name="djctl")
            ModulesManager.stop_module(module_name="webhook")
            ModulesManager.stop_module(module_name="twitch")
            ModulesManager.stop_module(module_name="podcast")
            ModulesManager.stop_module(module_name="twinkly")
            logging.info(f"Exiting...\n")
            return 0
        if command == "status":
            ModulesManager.get_module_status()
        if command.startswith("start "):
            ModulesManager.start_module(module_name=command[6:])
        if command.startswith("stop "):
            ModulesManager.stop_module(module_name=command[5:])
        if command.startswith("restart "):
            ModulesManager.stop_module(module_name=command[8:])
            ModulesManager.start_module(module_name=command[6:])
        if command == "stop event":
            logging.info(f"Cannot stop event loop. Exit application instead")
        if command.startswith("event "):
            AsyncioThread.run_coroutine(
                EventModule.queue_event(event=command[6:])
            )
        return 1
