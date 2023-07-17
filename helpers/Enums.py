from enum import Enum


class ThreadState(Enum):
    IDLE = 0
    RUNNING = 1
    STOPPING = 2


class ModuleStatus(Enum):
    IDLE = 0
    RUNNING = 1
    STOPPING = 2


class Status(Enum):
    DISABLED = 0
    ENABLED = 1


class OBSConnectionStatus(Enum):
    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTING = 2
    DISCONNECTING = 3


class QueueStatus(Enum):
    IDLE = 0
    PROCESSING = 1


class ModuleRole(Enum):
    LEADER = 0
    FOLLOWER = 1
    DISPLAY = 2

    @staticmethod
    def function(role_name: str):
        try:
            return ModuleRole[role_name.upper()]
        except KeyError:
            raise ValueError(f"Invalid function value: {role_name}")


class ConversationStatus(Enum):
    IDLE = 0
    OCCUPIED = 1


class TwinklyEffect(Enum):
    RAINBOW = 0
    SNOW = 1
    COLLIDE = 2
    FIREWORK = 3
    USA = 4


class TwinklyReact(Enum):
    VU_METER = "00000000-0000-0000-0000-000000000001"
    BEAT_HUE = "00000000-0000-0000-0000-000000000002"
    PSYCHEDELICA = "00000000-0000-0000-0000-000000000003"
    RED_VERTIGO = "00000000-0000-0000-0000-000000000004"
    DANCING_BANDS = "00000000-0000-0000-0000-000000000005"
    DIAMOND_SWIRL = "00000000-0000-0000-0000-000000000006"
    JOYFUL_STRIPES = "00000000-0000-0000-0000-000000000007"
    ELEVATOR = "00000000-0000-0000-0000-000000000008"
    ANGEL_FADE = "00000000-0000-0000-0000-000000000009"
    CLOCKWORK = "00000000-0000-0000-0000-00000000000A"
    SIPARIO = "00000000-0000-0000-0000-00000000000B"
    SUNSET = "00000000-0000-0000-0000-00000000000C"

    @classmethod
    def index(cls, member):
        return list(cls).index(member)

    @classmethod
    def id(cls, index: int = 0):
        return list(cls)[index]


class TwinklyPlaylist(Enum):
    FIRE = 0
    LOVE = 1
    GREEN_WAVES = 2
    RAINBOW_WAVES = 3
    I_LOVE_YOU = 4


class StableDiffusionStyles(Enum):
    GHIBLI = "Ghibli"
    VECTOR = "Vector Illustrations"
    DIGITAL = "Digital/Oil Painting"
    GAME = "Indie Game"
    PHOTO = "Original Photo Style"
    NOIR = "Black and White Film Noir"
    ISOMETRIC = "Isometric Rooms"
    HOLOGRAM = "Space Hologram"
    CUTE = "Cute Creatures"
    PORTRAIT = "Realistic Photo Portraits"
    SCENIC = "Professional Scenic Photographs"
    MANGA = "Manga"
    ANIME = "Anime"


class TwinklyMusic(Enum):
    DANCE_SHUFFLE = (0, -1)  # 0
    DANCE_NOVA = (0, 0)  # 1
    DANCE_OMEGA = (0, 1)  # 2
    DANCE_DIAMOND_WEAVE = (0, 2)  # 3
    DANCE_OSCILLATOR = (0, 3)  # 4
    DANCE_MARCH = (0, 4)  # 5
    DANCE_PSYCHO_MARCH = (0, 5)  # 6
    DANCE_CHEVRON = (0, 6)  # 7

    CLASSIC_SHUFFLE = (1, -1)  # 8
    CLASSIC_CANDY_LINE = (1, 0)  # 9
    CLASSIC_SWIRL = (1, 1)  # 10
    CLASSIC_WEAVE = (1, 2)  # 11
    CLASSIC_FIZZ = (1, 3)  # 12
    CLASSIC_VU_METER = (1, 4)  # 13
    CLASSIC_RADIATE = (1, 5)  # 14
    CLASSIC_DIAMOND_TWIST = (1, 6)  # 15
    CLASSIC_PSYCHO_SPARKLE = (1, 7)  # 16

    AMBIENT_SHUFFLE = (2, -1)  # 17
    AMBIENT_SPARKLES = (2, 0)  # 18
    AMBIENT_TRANQUIL = (2, 1)  # 19
    AMBIENT_SPARKLES_2 = (2, 2)  # 20
    AMBIENT_PLASMA = (2, 3)  # 21

    FLUO_SHUFFLE = (3, -1)  # 22
    FLUO_PSYCHEDELIC = (3, 0)  # 23
    FLUO_VU_FLUO = (3, 1)  # 24
    FLUO_CROSSOVER = (3, 2)  # 25
    FLUO_AMPLIFY = (3, 3)  # 26
    FLUO_ZIP = (3, 4)  # 27
    FLUO_SUNRAY = (3, 5)  # 28

    CHILLOUT_SHUFFLE = (4, -1)  # 29
    CHILLOUT_SPARKLES = (4, 0)  # 30
    CHILLOUT_BUBBLES = (4, 1)  # 31
    CHILLOUT_PSYCHO_SPARKLES = (4, 2)  # 32
    CHILLOUT_NOVA = (4, 3)  # 33

    POP_SHUFFLE = (5, -1)  # 34
    POP_BPM_HUE = (5, 0)  # 35
    POP_VU_FREQ = (5, 1)  # 36
    POP_BOUNCE = (5, 2)  # 37
    POP_ANGEL_FADE = (5, 3)  # 38
    POP_CLOCKWORK = (5, 4)  # 39
    POP_SIGNAL = (5, 5)  # 40
    POP_OSCILLATOR = (5, 6)  # 41

    @classmethod
    def index(cls, member):
        return list(cls).index(member)

    @classmethod
    def id(cls, index: int = 0):
        return list(cls)[index]
