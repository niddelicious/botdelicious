import asyncio
from threading import Thread
from modules.DJctl import DJctl
from modules.OBS import OBS
from modules.TwitchChat import TwitchChat
from modules.Webhook import Webhook


class ModuleManager:
    def __init__(self, parent):
        self.parent = parent
        self.modules = parent.modules
        self.threads = parent.threads

    def startModule(self, moduleName=None, eventLoop=None):
        threadName = moduleName.capitalize()
        moduleStartFunctionName = f"start{moduleName.capitalize()}"
        moduleStartFunction = getattr(self, moduleStartFunctionName)
        eventLoop = asyncio.new_event_loop() if eventLoop is True else None
        self.threads[moduleName] = Thread(
            target=moduleStartFunction, name=threadName, args=(eventLoop,), daemon=True
        )
        self.threads[moduleName].start()
        if eventLoop:
            eventLoop.stop()

    def startWebhook(self, *args, **kwargs):
        self.modules.webhook.module = Webhook(
            self.parent.config.webhook.port, eventHandler=self.parent.eventHandler
        )

    def stopWebhook(self, *args, **kwargs):
        if self.modules.has_key("webhook"):
            self.modules.webhook.module.stop()

    def startDjctl(self, *args, **kwargs):
        self.modules.djctl.module = DJctl()
        self.modules.djctl.module.console()

    def stopDjctl(self, *args, **kwargs):
        if self.modules.has_key("djctl"):
            self.modules.djctl.module.stop()

    def startObs(self, eventLoop: asyncio.AbstractEventLoop, *args, **kwargs):
        self.modules.obs.loop = eventLoop
        asyncio.set_event_loop(self.modules.obs.loop)
        self.modules.obs.loop.run_forever()
        self.modules.obs.module = OBS(
            self.parent.config.obs.port, self.parent.config.obs.password, name="obs"
        )
        self.modules.obs.loop.run_until_complete(self.modules.obs.module.connect())

    def stopObs(self, *args, **kwargs):
        if self.modules.has_key("obs"):
            self.modules.obs.loop.run_until_complete(
                self.modules.obs.module.disconnect()
            )

    def startPodcast(self, eventLoop: asyncio.AbstractEventLoop, *args, **kwargs):
        self.modules.podcast.loop = eventLoop
        asyncio.set_event_loop(self.modules.podcast.loop)
        self.modules.podcast.loop.run_forever()
        self.modules.podcast.module = OBS(
            self.parent.config.podcast.port,
            self.parent.config.podcast.password,
            name="podcast",
        )
        self.modules.podcast.loop.run_until_complete(
            self.modules.podcast.module.connect()
        )

    def stopPodcast(self, *args, **kwargs):
        if self.modules.has_key("podcast"):
            self.modules.podcast.loop.run_until_complete(
                self.modules.podcast.module.disconnect()
            )
            self.modules.podcast.module.stop()

    def startTwitch(self, eventLoop: asyncio.AbstractEventLoop, *args, **kwargs):
        asyncio.set_event_loop(eventLoop)
        eventLoop.run_forever()
        self.modules.twitch.module = TwitchChat(Bot=self)
        self.modules.twitch.module.run()

    def stopTwitch(self, *args, **kwargs):
        if self.modules.has_key("twitch"):
            self.modules.twitch.loop.run_until_complete(
                self.modules.twitch.module.close()
            )
            self.modules.twitch.loop.stop()
