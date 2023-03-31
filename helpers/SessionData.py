from datetime import datetime
import logging
from typing import List, Tuple

from dotmap import DotMap
from helpers.Dataclasses import Track, OBSText, Raid


class SessionData:
    _current_track = Track("Unknown", "Unknown")
    _playlist = []
    _start = None
    _comments_count = 0
    _tracks_count = 0
    _followers = []
    _raids = []
    _moderators = []
    _vips = []

    @classmethod
    def start_session(cls):
        cls._start = datetime.now()

    @classmethod
    def get_session_start(cls):
        if not cls._start:
            cls._start
        return cls._start

    @classmethod
    def get_current_track(cls):
        return DotMap(
            {
                "artist": cls._current_track.artist,
                "title": cls._current_track.title,
            }
        )

    @classmethod
    def tracks_count(cls):
        return cls._tracks_count

    @classmethod
    def comments_count(cls):
        return cls._comments_count

    @classmethod
    def add_comment(cls):
        cls._comments_count += 1

    @classmethod
    def add_raid(cls, raider: str = None, size: int = 0):
        cls._raids.append(Raid(raider, size))

    @classmethod
    def add_follower(cls, follower: str = None):
        cls._followers.append(follower)

    @classmethod
    def add_moderator(cls, moderator: str = None):
        cls._moderators.append(moderator)

    @classmethod
    def add_vip(cls, vip: str = None):
        cls._vips.append(vip)

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
        if cls._current_track not in cls._playlist:
            logging.debug(f"Adding track to session playlist")
            elapsed_time = round(
                (datetime.now() - cls.get_session_start()).total_seconds()
            )
            minutes, seconds = divmod(elapsed_time, 60)
            timestamp = f"{minutes:02d}:{seconds:02d}"
            track = Track(
                cls._current_track.artist, cls._current_track.title, timestamp
            )
            cls._playlist.append(track)
            cls._tracks_count += 1
            logging.debug(cls._playlist)

    @classmethod
    def get_playlist(cls) -> List[Track]:
        return cls._playlist

    @classmethod
    def get_followers(cls) -> List[str]:
        return cls._followers

    @classmethod
    def get_raids(cls) -> List[Tuple[str, int]]:
        return cls._raids

    @classmethod
    def get_moderators(cls) -> List[str]:
        return cls._moderators

    @classmethod
    def get_vips(cls) -> List[str]:
        return cls._vips


@classmethod
def process_session_credits(cls):
    credits = []
    _marker_y = 0
    _marker_x = 30
    _line = 40
    _header = 50
    _item = 60

    list_data = [
        ("Setlist", "Elements: Credits", "get_playlist"),
        ("Followers", "Elements: Credits", "get_followers"),
        ("Raids", "Elements: Credits", "get_raids"),
        ("Moderators", "Elements: Credits", "get_moderators"),
    ]

    for list_type, credit_type, method_name in list_data:
        lst = getattr(cls, method_name)() or []
        if lst:
            credits.append(
                OBSText(
                    credit_type,
                    f"{list_type}, header",
                    f"{list_type}:",
                    _marker_x,
                    _marker_y,
                    1400,
                    _line,
                )
            )
            _marker_y += _header
            section_text, section_height = cls.process_list_for_credits(
                lst, _line
            )
            credits.append(
                OBSText(
                    credit_type,
                    f"{list_type}, list",
                    section_text,
                    _marker_x,
                    _marker_y,
                    1400,
                    section_height,
                )
            )
            _marker_y += section_height
            _marker_y += _item

    return credits


@classmethod
def process_list_for_credits(
    cls, lst: List = None, line_height: int = None
) -> Tuple[str, int]:
    text = ""
    height = 0
    for item in lst:
        text = text + f"{item}\n"
        height += line_height
    return text, height
