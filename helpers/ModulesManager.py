import logging
from AsyncioThread import AsyncioThread
from helpers.ConfigManager import ConfigManager
from modules.DJctl import DJctl
from modules.OBS import OBS
from modules.TwitchChat import TwitchChat
from modules.Webhook import Webhook
from modules.Event import EventModule


class ModulesManager:
    def __init__(cls):
        pass

    def startModule(cls, moduleName=None):
        module = getattr(cls.modules, moduleName)
        AsyncioThread.run_coroutine(module.start())

    def stopModule(cls, moduleName=None):
        module = getattr(cls.modules, moduleName)
        AsyncioThread.run_coroutine(module.stop())

    async def startEvent(cls, *args, **kwargs):
        cls.modules.event.module = EventModule()
        cls.modules.event.module.start()
        AsyncioThread.run_coroutine(cls.modules.event.module.run())

    async def stopEvent(cls, *args, **kwargs):
        if cls.modules.has_key("event"):
            cls.modules.event.module.stop()

    async def startWebhook(cls, *args, **kwargs):
        cls.modules.webhook.module = Webhook(
            port=ConfigManager.config.webhook.port
        )

    async def stopWebhook(cls, *args, **kwargs):
        logging.debug("stopping webhook")
        logging.debug(cls.modules)
        if cls.modules.has_key("webhook"):
            cls.modules.webhook.module.stop()

    async def startDjctl(cls, *args, **kwargs):
        cls.modules.djctl.module = DJctl()
        cls.modules.djctl.module.console()

    async def stopDjctl(cls, *args, **kwargs):
        if cls.modules.has_key("djctl"):
            cls.modules.djctl.module.stop()

    async def startObs(cls, *args, **kwargs):
        cls.modules.obs.module = OBS(
            ConfigManager.config.obs.port,
            ConfigManager.config.obs.password,
            name="obs",
        )
        AsyncioThread.run_coroutine(cls.modules.obs.module.connect())

    async def stopObs(cls, *args, **kwargs):
        if cls.modules.has_key("obs"):
            AsyncioThread.run_coroutine(cls.modules.obs.module.disconnect())

    async def startPodcast(cls, *args, **kwargs):
        cls.modules.podcast.module = OBS(
            ConfigManager.config.podcast.port,
            ConfigManager.config.podcast.password,
            name="podcast",
        )
        AsyncioThread.run_coroutine(cls.modules.podcast.module.connect())

    async def stopPodcast(cls, *args, **kwargs):
        if cls.modules.has_key("podcast"):
            AsyncioThread.run_coroutine(
                cls.modules.podcast.module.disconnect()
            )
            cls.modules.podcast.module.stop()

    async def startTwitch(cls, *args, **kwargs):
        cls.modules.twitch.module = TwitchChat()
        AsyncioThread.run_coroutine(cls.modules.twitch.module.start())

    async def stopTwitch(cls, *args, **kwargs):
        if cls.modules.has_key("twitch"):
            AsyncioThread.run_coroutine(cls.modules.twitch.module.close())
