import enum


class ThreadState(enum.Enum):
    IDLE = 0
    RUNNING = 1
    STOPPING = 2


class ModuleStatus(enum.Enum):
    IDLE = 0
    RUNNING = 1
    STOPPING = 2


class QueueStatus(enum.Enum):
    IDLE = 0
    PROCESSING = 1
