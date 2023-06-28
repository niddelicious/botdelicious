import logging

from datetime import datetime
from typing import List, Tuple
from dotmap import DotMap

from Helpers.Dataclasses import Track, OBSText, Raid


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
    _chatters = []
    _tokens_count = 0

    @classmethod
    def start_session(cls):
        cls._start = datetime.now()

    @classmethod
    def get_session_start(cls):
        if not cls._start:
            cls.start_session()
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
    def followers_count(cls):
        return len(cls._followers)

    @classmethod
    def raids_count(cls):
        return len(cls._raids)

    @classmethod
    def moderators_count(cls):
        return len(cls._moderators)

    @classmethod
    def vips_count(cls):
        return len(cls._vips)

    @classmethod
    def tokens_count(cls):
        return cls._tokens_count

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
    def add_chatter(cls, chatter: str = None):
        cls._chatters.append(chatter)

    @classmethod
    def add_tokens(cls, tokens: int = 0):
        cls._tokens_count += tokens
        logging.debug(f"Used tokens: {tokens} - Total: {cls._tokens_count}")

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
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            timestamp = (
                f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                if hours > 0
                else f"{minutes:02d}:{seconds:02d}"
            )
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
    def get_chatters(cls) -> List[str]:
        return cls._chatters

    @classmethod
    def write_playlist_to_file(cls):
        filename = f"playlist, {cls._start.strftime('%Y-%m-%d %H.%M')}.txt"
        with open(filename, "w") as file:
            for track in cls._playlist:
                file.write(
                    f"[{track.timestamp}] {track.artist} - {track.title}\n"
                )

    @classmethod
    def process_session_credits(cls):
        credits = []
        _marker_y = 0
        _marker_x = 0
        _line = 40
        _header = 50
        _item = 60
        _width = 1500

        list_data = [
            ("Setlist", "Elements: Credits texts", "get_playlist"),
            ("Followers", "Elements: Credits texts", "get_followers"),
            ("Raids", "Elements: Credits texts", "get_raids"),
            ("Moderators", "Elements: Credits texts", "get_moderators"),
        ]

        for list_type, credit_type, method_name in list_data:
            lst = getattr(cls, method_name)() or []
            if lst:
                credits.append(
                    OBSText(
                        scene=credit_type,
                        source=f"{list_type}, header",
                        text=f"{list_type}:",
                        position_x=_marker_x,
                        position_y=_marker_y,
                        width=_width,
                        height=_line,
                    )
                )
                _marker_y += _header
                section_text, section_height = cls.process_list_for_credits(
                    lst, _line, _item
                )
                credits.append(
                    OBSText(
                        scene=credit_type,
                        source=f"{list_type}, list",
                        text=section_text,
                        position_x=_marker_x,
                        position_y=_marker_y,
                        width=_width,
                        height=section_height,
                    )
                )
                _marker_y += section_height

        return credits

    @classmethod
    def process_list_for_credits(
        cls, lst: List = None, line_height: int = None, bottom_margin: int = 0
    ) -> Tuple[str, int]:
        text = ""
        height = 0
        for item in lst:
            text = text + f"{item}\n"
            height += line_height
        height += bottom_margin
        return text, height
