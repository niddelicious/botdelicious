import json
import logging
import webhook_listener

from dotmap import DotMap

from helpers.AbstractModule import BotdeliciousModule


class Webhook(BotdeliciousModule):
    def __init__(self, port: str = "8080", parent=None):
        super().__init__()
        self.parent = parent
        self.webhookListener = webhook_listener.Listener(
            handlers={"POST": self.incomingWebhook},
            port=port,
        )
        self.webhookListener.start()

    def start(self):
        pass

    def status(self):
        return self.status

    def incomingWebhook(self, request, *args, **kwargs):
        logging.debug("Incoming Webhook")
        logging.debug(request)
        if args and (destination := getattr(self, args[0], None)):
            destination(webhookData=DotMap(json.loads(request.body.read())))
        return

    def djctl(self, webhookData: DotMap = None):
        eventHandler = self.parent.getEventHandler()
        self.parent.run_asyncio_coroutine(
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
