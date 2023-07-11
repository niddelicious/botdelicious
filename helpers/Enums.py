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
