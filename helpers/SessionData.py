from datetime import datetime
import logging
from typing import List, Tuple

from dotmap import DotMap
from helpers.Dataclasses import Track, OBSText


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
        cls._raids.append((raider, size))

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

        if cls.get_playlist():
            credits.append(
                OBSText(
                    "Elements: Credits",
                    "Setlist, header",
                    "Setlist:",
                    _marker_x,
                    _marker_y,
                    1400,
                    _line,
                )
            )
            _marker_y += _header
            setlist_text = ""
            setlist_height = 0
            for track in cls.get_playlist():
                setlist_text = (
                    setlist_text + f"{track.artist} - {track.title}\n"
                )
                setlist_height += _line
            credits.append(
                OBSText(
                    "Elements: Credits",
                    "Setlist, list",
                    setlist_text,
                    _marker_x,
                    _marker_y,
                    1400,
                    setlist_height,
                )
            )
            _marker_y += setlist_height
            _marker_y += _item

        if cls.get_followers():
            credits.append(
                OBSText(
                    "Elements: Credits",
                    "Followers, header",
                    "Followers:",
                    _marker_x,
                    _marker_y,
                    1400,
                    _line,
                )
            )
            _marker_y += _header
            followers_text = ""
            followers_height = 0
            for follower in cls.get_followers():
                followers_text = followers_text + f"{follower}\n"
                followers_height += _line
            credits.append(
                OBSText(
                    "Elements: Credits",
                    "Followers, list",
                    followers_text,
                    _marker_x,
                    _marker_y,
                    1400,
                    followers_height,
                )
            )
            _marker_y += followers_height
            _marker_y += _item

        if cls.get_raids():
            credits.append(
                OBSText(
                    "Elements: Credits",
                    "Raids, header",
                    "Raids:",
                    _marker_x,
                    _marker_y,
                    1400,
                    _line,
                )
            )
            _marker_y += _header
            raids_text = ""
            raids_height = 0
            for raid in cls.get_raids():
                raids_text = raids_text + f"{raid[0]} x {raid[1]}\n"
                raids_height += _line
            credits.append(
                OBSText(
                    "Elements: Credits",
                    "Raids, list",
                    raids_text,
                    _marker_x,
                    _marker_y,
                    1400,
                    raids_height,
                )
            )
            _marker_y += raids_height
            _marker_y += _item

        if cls.get_moderators():
            credits.append(
                OBSText(
                    "Elements: Credits",
                    "Moderators, header",
                    "Moderators:",
                    _marker_x,
                    _marker_y,
                    1400,
                    _line,
                )
            )
            _marker_y += _header
            moderators_text = ""
            moderators_height = 0
            for moderator in cls.get_moderators():
                moderators_text = moderators_text + f"{moderator}\n"
                moderators_height += _line
            credits.append(
                OBSText(
                    "Elements: Credits",
                    "Moderators, list",
                    moderators_text,
                    _marker_x,
                    _marker_y,
                    1400,
                    moderators_height,
                )
            )
            _marker_y += moderators_height
            _marker_y += _item

        return credits
