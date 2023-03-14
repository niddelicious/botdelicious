from datetime import datetime
from typing import Dict
from dataclasses import dataclass


@dataclass
class Track:
    artist: str
    title: str
    timestamp: str = None

    def __hash__(self):
        return hash((self.artist, self.title))

    def __eq__(self, other):
        if isinstance(other, Track):
            return self.artist == other.artist and self.title == other.title
        return False
