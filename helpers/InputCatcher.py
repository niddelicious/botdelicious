import logging

from helpers.ModulesManager import ModulesManager


class InputCatcher:
    @classmethod
    def commandline(cls):
        command = input("Command: \n")
        if command == "exit":
            ModulesManager.stop_module(module_name="webhook")
            ModulesManager.stop_module(module_name="chat")
            ModulesManager.stop_module(module_name="twitch")
            ModulesManager.stop_module(module_name="podcast")
            ModulesManager.stop_module(module_name="djctl")
            ModulesManager.stop_module(module_name="twinkly")
            logging.info(f"Exiting...\n")
            return 0
        if command == "start twitch":
            ModulesManager.start_module(module_name="twitch")
        if command == "stop twitch":
            ModulesManager.stop_module(module_name="twitch")
        if command == "start event":
            ModulesManager.start_module(module_name="event")
        if command == "stop event":
            logging.info(f"Cannot stop event loop. Exit application instead")
        if command == "start webhook":
            ModulesManager.start_module(module_name="webhook")
        if command == "stop webhook":
            ModulesManager.stop_module(module_name="webhook")
        if command == "start djctl":
            ModulesManager.start_module(module_name="djctl")
        if command == "stop djctl":
            ModulesManager.stop_module(module_name="djctl")
        if command == "start chat":
            ModulesManager.start_module(module_name="chat")
        if command == "stop chat":
            ModulesManager.stop_module(module_name="chat")
        if command == "start podcast":
            ModulesManager.start_module(module_name="podcast")
        if command == "stop podcast":
            ModulesManager.stop_module(module_name="podcast")
        if command == "start lights":
            ModulesManager.start_module(module_name="twinkly")
        if command == "stop lights":
            ModulesManager.stop_module(module_name="twinkly")
        return 1
