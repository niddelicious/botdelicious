from datetime import datetime
from typing import Dict
from dotmap import DotMap


class SessionData:
    _current_track = DotMap({"artist": "Unknown", "title": "Unknown"})
    _session_playlist = []
    _session_setlist = []
    _session_start = None

    @classmethod
    def start_session(cls):
        cls.start_session = datetime.now()

    @classmethod
    def get_current_track(cls):
        return cls._current_track

    @classmethod
    def get_current_artist(cls):
        return cls._current_track.artist

    @classmethod
    def get_current_title(cls):
        return cls._current_track.title

    @classmethod
    def set_current_track(
        cls,
        track_info: Dict[str, str] = {"artist": "Unknown", "title": "Unknown"},
    ):
        cls._current_track = DotMap(track_info)
        cls.add_current_track_to_session_playlist()

    @classmethod
    def add_current_track_to_session_playlist(cls):
        if cls._current_track not in cls._session_playlist:
            cls._session_playlist.append(cls._current_track)

            elapsed_time = (datetime.now() - cls._session_start).seconds
            minutes, seconds = divmod(elapsed_time, 60)
            timestamp = f"{minutes}:{seconds}"
            cls._session_setlist.append(
                {**cls._current_track, "timestamp": timestamp}
            )

    @classmethod
    def get_session_playlist(cls):
        return cls._session_playlist
