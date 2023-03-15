from datetime import datetime
import logging
from typing import List

from dotmap import DotMap
from helpers.Dataclasses import Track


class SessionData:
    _current_track = Track("Unknown", "Unknown")
    _session_playlist = []
    _session_start = None
    _number_of_comments = 0
    _number_of_tracks = 0

    @classmethod
    def start_session(cls):
        cls._session_start = datetime.now()

    @classmethod
    def get_session_start(cls):
        if not cls._session_start:
            cls._session_start
        return cls._session_start

    @classmethod
    def get_current_track(cls):
        return DotMap(
            {
                "artist": cls._current_track.artist,
                "title": cls._current_track.title,
            }
        )

    @classmethod
    def number_of_tracks(cls):
        return cls._number_of_tracks

    @classmethod
    def number_of_comments(cls):
        return cls._number_of_comments

    @classmethod
    def add_comment(cls):
        cls._number_of_comments += 1

    @classmethod
    def current_artist(cls):
        return cls._current_track.artist

    @classmethod
    def current_title(cls):
        return cls._current_track.title

    @classmethod
    def set_current_track(cls, artist: str, title: str):
        logging.debug(f"Setting current track: {artist} - {title}")
        cls._current_track = Track(artist, title)
        cls.add_current_track_to_session_playlist()

    @classmethod
    def add_current_track_to_session_playlist(cls):
        if cls._current_track not in cls._session_playlist:
            logging.debug(f"Adding track to session playlist")
            elapsed_time = round(
                (datetime.now() - cls.get_session_start()).total_seconds()
            )
            minutes, seconds = divmod(elapsed_time, 60)
            timestamp = f"{minutes:02d}:{seconds:02d}"
            track = Track(
                cls._current_track.artist, cls._current_track.title, timestamp
            )
            cls._session_playlist.append(track)
            cls._number_of_tracks += 1
            logging.debug(cls._session_playlist)

    @classmethod
    def get_session_playlist(cls) -> List[Track]:
        return cls._session_playlist
