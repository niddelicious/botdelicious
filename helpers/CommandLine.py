import logging
from AsyncioThread import AsyncioThread

from Controllers.ModulesController import ModulesController
from Modules.ChatModule import _TwitchBot
from Modules.EventModule import EventModule
import logging


class CommandLine:
    @classmethod
    def cli(cls):
        command = input("Command: \n")
        if command == "exit":
            ModulesController.stop_module(module_name="chat")
            ModulesController.stop_module(module_name="djctl")
            ModulesController.stop_module(module_name="webhook")
            ModulesController.stop_module(module_name="twitch")
            ModulesController.stop_module(module_name="podcast")
            ModulesController.stop_module(module_name="twinkly")
            logging.info(f"Exiting...\n")
            return 0
        if command == "status":
            ModulesController.get_module_status()
        if command.startswith("start "):
            ModulesController.start_module(module_name=command[6:])
        if command.startswith("stop "):
            if command[5:] == "event":
                logging.info(
                    f"Cannot stop event loop. Exit application instead"
                )
            else:
                ModulesController.stop_module(module_name=command[5:])
        if command.startswith("restart "):
            ModulesController.stop_module(module_name=command[8:])
            ModulesController.start_module(module_name=command[8:])
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
            text_avatar_url = "https://loremflickr.com/300/300/twitch"
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
                        avatar_url=text_avatar_url,
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
            if command[5:] == "tune":
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(event="tune")
                )
            if command[5:] == "midjourney":
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(
                        event="switch_scene",
                        scene_name="Scene: Midjourney",
                    )
                )
            if command[5:] == "vip":
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(event="vip", vip="vip_name")
                )
            if command[5:12] == "chatter":
                chatter_name = command[13:]
                AsyncioThread.run_coroutine(
                    _TwitchBot.chatter_active(chatter=chatter_name)
                )
            if command[5:] == "follower":
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(
                        event="new_follower",
                        username="new_follower_name",
                        avatar_url=text_avatar_url,
                    )
                )
            if command[5:] == "raid":
                AsyncioThread.run_coroutine(
                    EventModule.queue_event(
                        event="raid",
                        name="new_raid_name",
                        count=256,
                        avatar_url=text_avatar_url,
                    )
                )
            if command[5:] == "credits":
                from Tests.test_session_data import test_session_data

                test_session_data()

        return 1
