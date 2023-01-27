import enum


class ThreadState(enum.Enum):
    IDLE = 0
    RUNNING = 1
    STOPPING = 2
