import time

from .MemoryID import MemoryID


def time_usec() -> int:
    return int(time.time() * 1e6)
