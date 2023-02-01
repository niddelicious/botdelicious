import logging


class MessageHandler:
    def __init__(self, modules=None) -> None:
        self.modules = modules
        pass

    def handleNewTrack(self, artist: str, title: str):
        logging.info(f"Handle new track:")
        logging.info(f"Artist: {artist} | Title: {title}")
        self.modules.obs.loop.run_until_complete(
            self.modules.obs.module.changeSmallTrackInfoAndDisplayElement(artist, title)
        )
