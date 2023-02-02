import logging


class EventHandler:
    def __init__(self, modules=None) -> None:
        self.modules = modules
        pass

    def handleNewTrack(self, artist: str, title: str):
        logging.info(f"Handle new track:")
        logging.info(f"Artist: {artist} | Title: {title}")
        self.modules.obs.loop.run_until_complete(
            self.modules.obs.module.changeSmallTrackInfoAndThenDisplayElement(
                artist, title
            )
        )
        self.modules.podcast.loop.run_until_complete(
            self.modules.podcast.module.displayElementThenChangeSmallTrackInfo(
                artist, title
            )
        )
