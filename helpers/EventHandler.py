import asyncio
import logging
import shutil


class EventHandler:
    def __init__(self, modules=None) -> None:
        self.modules = modules
        self.queue = asyncio.Queue()

    def handleEvent(self, event: str = None, **kwargs):
        eventHandler = "handle_" + event
        if hasattr(self, eventHandler):
            handler = getattr(self, eventHandler)
            handler(**kwargs)
        pass

    def handle_newTrack(
        self,
        artist: str = None,
        title: str = None,
        containsCoverArt: bool = False,
        *args,
        **kwargs,
    ):
        logging.info(f"Handle new track:")
        logging.info(f"Artist: {artist} | Title: {title}")
        logging.info(f"Cover art: {containsCoverArt}")
        if not containsCoverArt:
            self.copyFallbackImageToCoverFile()
        logging.info(f"{self.modules}")
        self.modules.obs.loop.run_until_complete(
            self.modules.obs.module.eventUpdateSmallTrackInfoThenTriggerSlideAnimation(
                artist, title
            )
        )
        self.modules.podcast.loop.run_until_complete(
            self.modules.podcast.module.eventTriggerSlideAnimationThenUpdateSmallTrackInfo(
                artist, title
            )
        )

    def copyFallbackImageToCoverFile(self):
        shutil.copy2(
            "external/djctl/record-vinyl-solid-light.png",
            "external/djctl/latest-cover-art.png",
        )
