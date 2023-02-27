import json
import logging
import webhook_listener

from dotmap import DotMap
from AsyncioThread import AsyncioThread

from helpers.AbstractModule import BotdeliciousModule
from helpers.ConfigManager import ConfigManager
from helpers.Enums import ModuleStatus
from main import Botdelicious


class Webhook(BotdeliciousModule):
    STATUS = ModuleStatus.IDLE

    def __init__(self):
        super().__init__()
        self.webhookListener = webhook_listener.Listener(
            handlers={"POST": self.incomingWebhook},
            port=ConfigManager.config.webhook.port,
        )

    def start(self):
        self.STATUS = ModuleStatus.RUNNING
        self.webhookListener.start()

    def status(self):
        return self.STATUS

    def stop(self):
        self.STATUS = ModuleStatus.STOPPING
        self.webhookListener.stop()
        self.STATUS = ModuleStatus.IDLE

    def incomingWebhook(self, request, *args, **kwargs):
        logging.debug("Incoming Webhook")
        logging.debug(request)
        if args and (destination := getattr(self, args[0], None)):
            destination(webhookData=DotMap(json.loads(request.body.read())))
        return

    def djctl(self, webhookData: DotMap = None):
        eventHandler = Botdelicious.getEventHandler()
        AsyncioThread.run_coroutine(
            eventHandler.queueEvent(
                event="newTrack",
                artist=webhookData.data.artist,
                title=webhookData.data.title,
                containsCoverArt=webhookData.cover.art,
            )
        )

    def stop(self):
        logging.debug("Stopping webhookListener")
        self.webhookListener.stop()
