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

    def __str__(self) -> str:
        return f"{self.artist} - {self.title}"


@dataclass
class OBSText:
    scene: str
    source: str
    text: str
    position_x: int
    position_y: int
    width: int
    height: int


@dataclass
class Raid:
    name: str
    size: int

    def __str__(self) -> str:
        return f"{self.name} x {self.size}"
