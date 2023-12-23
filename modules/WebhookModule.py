import json
import logging
import random
import webhook_listener

from dotmap import DotMap
from AsyncioThread import AsyncioThread

from Modules.BotdeliciousModule import BotdeliciousModule
from Controllers.ConfigController import ConfigController
from Helpers.Enums import ModuleStatus, VideoBeeple, VideoYule, VideoTrippy
from Modules.EventModule import EventModule


class WebhookModule(BotdeliciousModule):
    _status = ModuleStatus.IDLE

    def __init__(self):
        super().__init__()

    async def start(self):
        self.set_status(ModuleStatus.RUNNING)
        self._webhook_listener = webhook_listener.Listener(
            handlers={"POST": self.incoming_webhook},
            port=ConfigController._config.webhook.port,
        )
        self._webhook_listener.start()

    async def stop(self):
        self.set_status(ModuleStatus.STOPPING)
        self._webhook_listener.stop()
        self.set_status(ModuleStatus.IDLE)

    def incoming_webhook(self, request, *args, **kwargs):
        logging.debug("Incoming Webhook")
        logging.debug(request)
        if args and (destination := getattr(self, args[0], None)):
            destination(
                request,
                *args,
                **kwargs,
            )
        return

    def djctl(self, request, *args, **kwargs):
        body = DotMap(json.loads(request.body.read()))
        AsyncioThread.run_coroutine(
            EventModule.queue_event(
                event="new_track",
                artist=body.data.artist,
                title=body.data.title,
                contains_cover_art=body.cover.art,
            )
        )
        AsyncioThread.run_coroutine(
            EventModule.queue_event(event="show_small_track_id")
        )

        vj_loop_list = list(VideoBeeple) + list(VideoYule) + list(VideoTrippy)
        video_id = random.choice(range(len(vj_loop_list)))
        video_file = vj_loop_list[video_id]

        AsyncioThread.run_coroutine(
            EventModule.queue_event(
                event="change_video",
                video=video_file.value,
            )
        )

    def kofi(self, request, *args, **kwargs):
        kofi_data = json.loads(kwargs["data"])
        if kofi_data["verification_token"] != ConfigController._config.kofi.token:
            logging.warning("Kofi token does not match!")
            return
        logging.debug("Kofi token matches")
        AsyncioThread.run_coroutine(
            EventModule.queue_event(
                event="kofi",
                from_name=kofi_data["from_name"],
                type=kofi_data["type"],
                amount=kofi_data["amount"],
                currency=kofi_data["currency"],
                message=kofi_data["message"],
            )
        )
