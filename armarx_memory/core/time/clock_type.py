import enum


class ClockType(enum.Enum):
    Realtime = enum.auto()
    Monotonic = enum.auto()
    Virtual = enum.auto()
    Unknown = enum.auto()
