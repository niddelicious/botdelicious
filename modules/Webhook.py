import json
import logging
import webhook_listener
import shutil

from helpers.AbstractModule import BotdeliciousModule


class Webhook(BotdeliciousModule):
    def __init__(self, port, messageHandler=None):
        super().__init__(messageHandler=messageHandler)
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
        logging.info("Incoming Webhook")
        logging.info(request)
        if args and (destination := getattr(self, args[0], None)):
            destination(body=request.body.read())
        return

    def djctl(self, body: object = None):
        jsonified = json.loads(body)
        logging.info(jsonified)
        if not jsonified["cover"]["art"]:
            self.copyFallbackImageToCoverFile()
        self.messageHandler.handleNewTrack(
            jsonified["data"]["artist"], jsonified["data"]["title"]
        )

    def stop(self):
        self.webhookListener.stop()

    def copyFallbackImageToCoverFile(self):
        shutil.copy2(
            "external/djctl/record-vinyl-solid-light.png",
            "external/djctl/latest-cover-art.png",
        )
