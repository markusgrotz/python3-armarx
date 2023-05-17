import dataclasses as dc
import typing as ty
from enum import IntEnum

from armarx_memory.aron.aron_dataclass import AronDataclass, AronIntEnumDataclass

class ClockTypeEnum(IntEnum):
    Realtime = 0,
    Monotonic = 1,
    Virtual = 2,
    Unknown = 3

# @dc.dataclass
# class ClockType(AronIntEnumDataclass):
#     value: ClockTypeEnum = dc.field(default=ClockTypeEnum.Realtime)

@dc.dataclass
class Duration(AronDataclass):
    microSeconds: int = 0

@dc.dataclass
class Frequency(AronDataclass):
    cycleDuration: Duration = dc.field(default_factory=Duration)

@dc.dataclass
class DateTime(AronDataclass):
    timeSinceEpoch: Duration = dc.field(default_factory=Duration)
    clockType: int = 0
    hostname: str = ""

    def __post_init__(self):
        self.timeSinceEpoch = Duration(**self.timeSinceEpoch) if isinstance(self.timeSinceEpoch, dict) else self.timeSinceEpoch