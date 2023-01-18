import logging
import webhook_listener


class Webhook:
    def __init__(self, port):
        self.webhookListener = webhook_listener.Listener(
            handlers={"POST": self.incomingWebhook},
            port=port,
        )
        self.webhookListener.start()

    def incomingWebhook(self, request, *args, **kwargs):
        logging.info("- Got webhook...")
        logging.info(request)
        body = request.body.read()
        logging.info(body)
        return

    def stop(self):
        self.webhookListener.stop()
