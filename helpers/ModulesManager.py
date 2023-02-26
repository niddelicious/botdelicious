import asyncio
import logging
from modules.DJctl import DJctl
from modules.OBS import OBS
from modules.TwitchChat import TwitchChat
from modules.Webhook import Webhook
from modules.Event import EventModule


class ModulesManager:
    def __init__(self, parent):
        self.parent = parent
        self.modules = parent.modules

    def run_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def startModule(self, moduleName=None):
        moduleStartFunctionName = f"start{moduleName.capitalize()}"
        moduleStartFunction = getattr(self, moduleStartFunctionName)
        self.parent.run_asyncio_coroutine(moduleStartFunction())

    def stopModule(self, moduleName=None):
        moduleStopFunctionName = f"stop{moduleName.capitalize()}"
        moduleStopFunction = getattr(self, moduleStopFunctionName)
        self.parent.run_asyncio_coroutine(moduleStopFunction())

    async def startEvent(self, *args, **kwargs):
        self.modules.event.module = EventModule(parent=self.parent)
        self.modules.event.module.start()
        self.parent.run_asyncio_coroutine(self.modules.event.module.run())

    async def stopEvent(self, *args, **kwargs):
        if self.modules.has_key("event"):
            self.modules.event.module.stop()

    async def startWebhook(self, *args, **kwargs):
        self.modules.webhook.module = Webhook(
            port=self.parent.config.webhook.port, parent=self.parent
        )

    async def stopWebhook(self, *args, **kwargs):
        logging.debug("stopping webhook")
        logging.debug(self.modules)
        if self.modules.has_key("webhook"):
            self.modules.webhook.module.stop()

    async def startDjctl(self, *args, **kwargs):
        self.modules.djctl.module = DJctl()
        self.modules.djctl.module.console()

    async def stopDjctl(self, *args, **kwargs):
        if self.modules.has_key("djctl"):
            self.modules.djctl.module.stop()

    async def startObs(self, *args, **kwargs):
        self.modules.obs.module = OBS(
            self.parent.config.obs.port, self.parent.config.obs.password, name="obs"
        )
        self.parent.run_asyncio_coroutine(self.modules.obs.module.connect())

    async def stopObs(self, *args, **kwargs):
        if self.modules.has_key("obs"):
            self.parent.run_asyncio_coroutine(self.modules.obs.module.disconnect())

    async def startPodcast(self, *args, **kwargs):
        self.modules.podcast.module = OBS(
            self.parent.config.podcast.port,
            self.parent.config.podcast.password,
            name="podcast",
        )
        self.parent.run_asyncio_coroutine(self.modules.podcast.module.connect())

    async def stopPodcast(self, *args, **kwargs):
        if self.modules.has_key("podcast"):
            self.parent.run_asyncio_coroutine(self.modules.podcast.module.disconnect())
            self.modules.podcast.module.stop()

    async def startTwitch(self, *args, **kwargs):
        self.modules.twitch.module = TwitchChat(parent=self.parent)
        self.parent.run_asyncio_coroutine(self.modules.twitch.module.start())

    async def stopTwitch(self, *args, **kwargs):
        if self.modules.has_key("twitch"):
            self.modules.twitch.loop.run_until_complete(
                self.modules.twitch.module.close()
            )
            self.modules.twitch.loop.stop()
