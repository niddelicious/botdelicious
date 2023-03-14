from datetime import datetime
from typing import List

from dotmap import DotMap
from helpers.Dataclasses import Track


class SessionData:
    _current_track = Track("Unknown", "Unknown")
    _session_playlist = []
    _session_start = None

    @classmethod
    def start_session(cls):
        cls._session_start = datetime.now()

    @classmethod
    def get_current_track(cls):
        return DotMap(
            {
                "artist": cls._current_track.artist,
                "title": cls._current_track.title,
            }
        )

    @classmethod
    def set_current_track(cls, artist: str, title: str):
        cls._current_track = Track(artist, title)
        cls.add_current_track_to_session_playlist()

    @classmethod
    def add_current_track_to_session_playlist(cls):
        if cls._current_track not in cls._session_playlist:
            elapsed_time = (datetime.now() - cls._session_start).seconds
            minutes, seconds = divmod(elapsed_time, 60)
            timestamp = f"{minutes}:{seconds}"
            track = Track(
                cls._current_track.artist, cls._current_track.title, timestamp
            )
            cls._session_playlist.append(track)

    @classmethod
    def get_session_playlist(cls) -> List[Track]:
        return cls._session_playlist
