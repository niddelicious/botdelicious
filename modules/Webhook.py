import json
import logging
import webhook_listener

from dotmap import DotMap
from AsyncioThread import AsyncioThread

from helpers.AbstractModule import BotdeliciousModule
from helpers.ConfigManager import ConfigManager
from helpers.Enums import ModuleStatus
from modules.Event import EventModule


class WebhookModule(BotdeliciousModule):
    _status = ModuleStatus.IDLE

    def __init__(self):
        super().__init__()

    async def start(self):
        self._status = ModuleStatus.RUNNING
        self._webhook_listener = webhook_listener.Listener(
            handlers={"POST": self.incoming_webhook},
            port=ConfigManager._config.webhook.port,
        )
        self._webhook_listener.start()

    async def _status(self):
        return self._status

    async def stop(self):
        self._status = ModuleStatus.STOPPING
        self._webhook_listener.stop()
        self._status = ModuleStatus.IDLE

    def incoming_webhook(self, request, *args, **kwargs):
        logging.debug("Incoming Webhook")
        logging.debug(request)
        if args and (destination := getattr(self, args[0], None)):
            destination(webhook_data=DotMap(json.loads(request.body.read())))
        return

    def djctl(self, webhook_data: DotMap = None):
        AsyncioThread.run_coroutine(
            EventModule.queue_event(
                event="new_track",
                artist=webhook_data.data.artist,
                title=webhook_data.data.title,
                contains_cover_art=webhook_data.cover.art,
            )
        )
        AsyncioThread.run_coroutine(
            EventModule.queue_event(event="show_small_track_id")
        )

    def stop(self):
        logging.debug("Stopping webhookListener")
        self._webhook_listener.stop()
