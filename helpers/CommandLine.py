import logging
from AsyncioThread import AsyncioThread

from helpers.ModulesManager import ModulesManager
from modules.Event import EventModule
import logging


class CommandLine:
    @classmethod
    def cli(cls):
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
            if command[5:] == "event":
                logging.info(
                    f"Cannot stop event loop. Exit application instead"
                )
            else:
                ModulesManager.stop_module(module_name=command[5:])
        if command.startswith("restart "):
            ModulesManager.stop_module(module_name=command[8:])
            ModulesManager.start_module(module_name=command[8:])
        if command.startswith("event "):
            AsyncioThread.run_coroutine(
                EventModule.queue_event(event=command[6:])
            )
        if command == "help":
            logging.info(f"Commands:")
            logging.info(f"exit")
            logging.info(f"status")
            logging.info(f"start <module>")
            logging.info(f"stop <module>")
            logging.info(f"restart <module>")
            logging.info(f"event <event>")
        if command.startswith("log "):
            level = command[4:]
            if level == "debug":
                logging.getLogger().setLevel(logging.DEBUG)
                EventModule.set_loop_sleep(sleep_time=2)
            if level == "info":
                logging.getLogger().setLevel(logging.INFO)
                EventModule.set_loop_sleep()
            if level == "warning":
                logging.getLogger().setLevel(logging.WARNING)
                EventModule.set_loop_sleep()
            if level == "error":
                logging.getLogger().setLevel(logging.ERROR)
                EventModule.set_loop_sleep()
            if level == "critical":
                logging.getLogger().setLevel(logging.CRITICAL)
                EventModule.set_loop_sleep()
            set_level = logging.getLevelName(
                logging.getLogger().getEffectiveLevel()
            )
            logging.info(f"Log level set to {set_level}")
        if command.startswith("test"):
            if command[5:] == "moderator":
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(
                        event="moderator", moderator="moderator_name"
                    )
                )
            if command[5:] == "shoutout":
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(
                        event="shoutout",
                        username="shoutout_username",
                        message="Shoutout message to be displayed",
                        avatar_url="https://static-cdn.jtvnw.net/jtv_user_pictures/e6bb8945-a942-498c-9ce3-6fa5b6367085-profile_image-300x300.png",
                    )
                )
            if command[5:] == "track":
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(
                        event="new_track",
                        artist="Test Artist",
                        title="Test Title",
                        contains_cover_art=False,
                    )
                )
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(event="show_small_track_id")
                )
            if command[5:] == "fire":
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(event="fire")
                )
            if command[5:] == "midjourney":
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(
                        event="switch_scene",
                        scene_name="Scene: Midjourney",
                    )
                )
            if command[5:] == "follower":
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(
                        event="new_follower", username="new_follower_name"
                    )
                )
            if command[5:] == "credits":
                from Tests.test_session_data import test_session_data
                test_session_data()
                
                

        return 1
