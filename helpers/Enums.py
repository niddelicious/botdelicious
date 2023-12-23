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


class VideoBeeple(Enum):
    TWENTYFOURK = "beeple/24K.mp4"
    ANGULAR = "beeple/Angular.mp4"
    AQUAHALL = "beeple/Aquahall.mp4"
    BOKK = "beeple/Bokk.mp4"
    BREATH_CTRL = "beeple/Breath Ctrl.mp4"
    BROKCHRD = "beeple/Brokchrd.mp4"
    BUILT_EE = "beeple/Built.ee.mp4"
    CLEANROOM = "beeple/Cleanroom.mp4"
    CRYSBLAST = "beeple/Crysblast.mp4"
    CRYSTMOUNTS = "beeple/Crystmounts.mov"
    CUTTT = "beeple/Cuttt.mp4"
    DARK_VALLEY = "beeple/Dark Valley.mp4"
    DARKNET = "beeple/Darknet.mov"
    DIRTY_RIBBON = "beeple/Dirty Ribbon.mp4"
    DVDE = "beeple/Dvde.mp4"
    EXHAUST = "beeple/Exhaust.mov"
    FIBER_OPTICAL = "beeple/Fiber Optical.mp4"
    FLUFFF = "beeple/Flufff.mp4"
    GLASS_LADDER = "beeple/Glass Ladder.mp4"
    GLAUBOX = "beeple/Glaubox.mov"
    GOBO_V1 = "beeple/Gobo.v1.mp4"
    HEXXX = "beeple/Hexxx.mp4"
    HOMIE = "beeple/Homie.mp4"
    KEWBIC_FLOW = "beeple/Kewbic Flow.mov"
    LIGHTGRID = "beeple/Lightgrid.mov"
    MILKCAVE = "beeple/Milkcave.mp4"
    MOONVIRUS = "beeple/Moonvirus.mp4"
    OCTMESH = "beeple/Octmesh.mp4"
    OKKKK = "beeple/Okkkk.mp4"
    OUT_B = "beeple/Out-B.mp4"
    P_CRAWL = "beeple/P-Crawl.mp4"
    PINK_VYNIL = "beeple/Pink Vynil.mov"
    POXELS = "beeple/Poxels.mov"
    QUICKSILVER = "beeple/Quicksilver.mp4"
    REBALANCE = "beeple/Rebalance.mp4"
    REDGATE_V1 = "beeple/Redgate.v1.mp4"
    REDGATE_V2 = "beeple/Redgate.v2.mp4"
    SETTING_SUN = "beeple/Setting Sun.mp4"
    SIGNAL_BARREL = "beeple/Signal Barrel.mov"
    STEPS = "beeple/Steps.mp4"
    STRT = "beeple/Strt.mp4"
    T_HAWK = "beeple/T-Hawk.mp4"
    TECH_FUX = "beeple/Tech.fux.mp4"
    TENDRIL = "beeple/Tendril.mp4"
    UNPLUG = "beeple/Unplug.mp4"
    WINTER_FEELS = "beeple/Winter Feels.mp4"
    WORMHOLE = "beeple/Wormhole.mov"
    WRMMM = "beeple/Wrmmm.mp4"

    @classmethod
    def index(cls, member):
        return list(cls).index(member)

    @classmethod
    def id(cls, index: int = 0):
        return list(cls)[index]

class VideoYule(Enum):
    CHRISTMAS_CHESHIRE_2 = "sleepless_monk/yule/Christmas Cheshire 2.mov"
    CHRISTMAS_CHESHIRE_3 = "sleepless_monk/yule/Christmas Cheshire 3.mov"
    CHRISTMAS_CHESHIRE_4 = "sleepless_monk/yule/christmas cheshire 4.mov"
    CHRISTMAS_CHESHIRE_5 = "sleepless_monk/yule/Christmas Cheshire 5.mov"
    CHRISTMAS_CHESHIRE = "sleepless_monk/yule/Christmas Cheshire.mov"
    MUSHROOM_SANTA_2 = "sleepless_monk/yule/Mushroom Santa 2.mov"
    MUSHROOM_SANTA_3 = "sleepless_monk/yule/Mushroom Santa 3.mov"
    MUSHROOM_SANTA_4 = "sleepless_monk/yule/Mushroom Santa 4.mov"
    MUSHROOM_SANTA = "sleepless_monk/yule/Mushroom Santa.mov"
    SANTA_AMANITA = "sleepless_monk/yule/Santa Amanita.mov"
    SANTA_CLOSEUP_2 = "sleepless_monk/yule/Santa Closeup 2.mov"
    SANTA_CLOSEUP = "sleepless_monk/yule/Santa closeup.mov"
    SANTA_DOLL_2 = "sleepless_monk/yule/Santa Doll 2.mov"
    SANTA_DOLL_3 = "sleepless_monk/yule/Santa Doll 3.mov"
    SANTA_DOLL_4 = "sleepless_monk/yule/Santa Doll 4.mov"
    SANTA_DOLL_5 = "sleepless_monk/yule/Santa Doll 5.mov"
    SANTA_DOLL_6 = "sleepless_monk/yule/Santa Doll 6.mov"
    SANTA_DOLL_7 = "sleepless_monk/yule/Santa Doll 7.mov"
    SANTA_DOLL = "sleepless_monk/yule/Santa Doll.mov"
    YULE_CRITTER = "sleepless_monk/yule/yule critter.mov"
    YULE_DECOR_2 = "sleepless_monk/yule/Yule Decor 2.mov"
    YULE_DECOR_3 = "sleepless_monk/yule/yule decor 3.mov"
    YULE_DECOR_4 = "sleepless_monk/yule/yule decor 4.mov"
    YULE_GODDESS_2 = "sleepless_monk/yule/yule goddess 2.mov"
    YULE_GODDESS = "sleepless_monk/yule/Yule Goddess.mov"
    YULE_SPIRIT = "sleepless_monk/yule/Yule Spirit.mov"
    YULE_TREE_2 = "sleepless_monk/yule/Yule Tree 2.mov"
    YULE_TREE_3 = "sleepless_monk/yule/Yule Tree 3.mov"
    YULE_TREE_4 = "sleepless_monk/yule/Yule Tree 4.mov"
    YULE_TREE_5 = "sleepless_monk/yule/Yule Tree 5.mov"
    YULE_TREE = "sleepless_monk/yule/Yule Tree.mov"
    YULE_TREECRITTER = "sleepless_monk/yule/Yule Treecritter.mov"

    @classmethod
    def index(cls, member):
        return list(cls).index(member)

    @classmethod
    def id(cls, index: int = 0):
        return list(cls)[index]

class VideoTrippy(Enum):
    AMANITA_2 = "sleepless_monk/trippy/Amanita 2.mov"
    AMANITA_3 = "sleepless_monk/trippy/Amanita 3.mov"
    AMANITA_4 = "sleepless_monk/trippy/Amanita 4.mov"
    AMANITA_5 = "sleepless_monk/trippy/Amanita 5.mov"
    AMANITA_6 = "sleepless_monk/trippy/Amanita 6.mov"
    AMANITA_7 = "sleepless_monk/trippy/amanita 7.mov"
    AMANITA = "sleepless_monk/trippy/Amanita.mov"
    BIRD_MORPH_2 = "sleepless_monk/trippy/Bird Morph 2.mov"
    BIRD_MORPH_3 = "sleepless_monk/trippy/bird morph 3.mov"
    BIRD_MORPH_5 = "sleepless_monk/trippy/bird morph 5.mov"
    BIRD_MORPH = "sleepless_monk/trippy/Bird Morph.mov"
    CHESHIRE_CAT_2 = "sleepless_monk/trippy/Cheshire cat 2.mov"
    CHESHIRE_CAT = "sleepless_monk/trippy/Cheshire Cat.mov"
    CHESHIRE_PORTAL_2 = "sleepless_monk/trippy/Cheshire Portal 2.mov"
    CHESHIRE_PORTAL_3 = "sleepless_monk/trippy/Cheshire Portal 3.mov"
    CHESHIRE_PORTAL_4 = "sleepless_monk/trippy/Cheshire Portal 4.mov"
    CHESHIRE_PORTAL_5 = "sleepless_monk/trippy/Cheshire portal 5.mov"
    CHESHIRE_PORTAL_6 = "sleepless_monk/trippy/cheshire portal 6.mov"
    CHESHIRE_PORTAL = "sleepless_monk/trippy/Cheshire Portal.mov"
    EYE_DECOR = "sleepless_monk/trippy/Eye Decor.mov"
    EYENIMORPH = "sleepless_monk/trippy/Eyenimorph.mov"
    FLOWER_ANIMORPH = "sleepless_monk/trippy/flower animorph.mov"
    FRACTAL_OPENING_3 = "sleepless_monk/trippy/Fractal  opening 3.mov"
    FRACTAL_OPENING = "sleepless_monk/trippy/Fractal  Opening.mov"
    FRACTAL_OPENING_2 = "sleepless_monk/trippy/Fractal Opening 2.mov"
    FRACTAL_OPENING_4 = "sleepless_monk/trippy/fractal opening 4.mov"
    FRACTAL_OPENING_5 = "sleepless_monk/trippy/fractal opening 5.mov"
    FRACTAL_OPENING_6 = "sleepless_monk/trippy/Fractal Opening 6.mov"
    FRACTAL_OPENING_7 = "sleepless_monk/trippy/fractal opening 7.mov"
    FUNGAL_SPIRIT = "sleepless_monk/trippy/Fungal Spirit.mov"
    MANDALA_ANIMORPH = "sleepless_monk/trippy/Mandala animorph.mov"
    MANDALA_DECOR_3 = "sleepless_monk/trippy/mandala Decor 3.mov"
    MANDALA_DECOR_4 = "sleepless_monk/trippy/mandala Decor 4.mov"
    MANDALA_DECOR_5 = "sleepless_monk/trippy/mandala decor 5.mov"
    MANDALA_DECOR_6 = "sleepless_monk/trippy/mandala decor 6.mov"
    MANDALA_DECOR_7 = "sleepless_monk/trippy/mandala decor 7.mov"
    MANDALA_DECOR = "sleepless_monk/trippy/Mandala Decor.mov"
    MUSCARIA_10 = "sleepless_monk/trippy/Muscaria 10.mov"
    MUSCARIA_11 = "sleepless_monk/trippy/Muscaria 11.mov"
    MUSCARIA_12 = "sleepless_monk/trippy/muscaria 12.mov"
    MUSCARIA_13 = "sleepless_monk/trippy/muscaria 13.mov"
    MUSCARIA_14 = "sleepless_monk/trippy/muscaria 14.mov"
    MUSCARIA_2 = "sleepless_monk/trippy/Muscaria 2.mov"
    MUSCARIA_4 = "sleepless_monk/trippy/muscaria 4.mov"
    MUSCARIA_5 = "sleepless_monk/trippy/Muscaria 5.mov"
    MUSCARIA_6 = "sleepless_monk/trippy/Muscaria 6.mov"
    MUSCARIA_7 = "sleepless_monk/trippy/Muscaria 7.mov"
    MUSCARIA_8 = "sleepless_monk/trippy/Muscaria 8.mov"
    MUSCARIA_9 = "sleepless_monk/trippy/Muscaria 9.mov"
    MUSCARIA = "sleepless_monk/trippy/Muscaria.mov"

    @classmethod
    def index(cls, member):
        return list(cls).index(member)

    @classmethod
    def id(cls, index: int = 0):
        return list(cls)[index]

