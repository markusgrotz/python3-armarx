import socket
import time

import armarx_core
from armarx_core.ice_conversion.ice_converter import IceConverter
from armarx_core import slice_loader

slice_loader.load_armarx_slice("ArmarXCore", "core/time.ice")
from armarx.core.time.dto import DateTime
from armarx.core.time.dto.ClockType import ClockTypeEnum


MIN_LONG_CPP = -9223372036854775808
INVALID_TIME_USEC = MIN_LONG_CPP

# TODO: Add DateTime type corresponding to C++ type.

def time_usec() -> int:
    return int(time.time() * 1e6)


class DateTimeIceConverter(IceConverter):
    @classmethod
    def _import_dto(cls):
        return DateTime

    def _from_ice(self, dto: DateTime) -> int:
        return dto.timeSinceEpoch.microSeconds

    def _to_ice(self, bo: int) -> DateTime:
        dto = DateTime()
        dto.timeSinceEpoch.microSeconds = bo
        dto.clockType = ClockTypeEnum.Monotonic
        dto.hostname = socket.gethostname()
        return dto


if __name__ == "__main__":
    c = DateTimeIceConverter()
    bo = time_usec()
    dto = c.to_ice(bo)
    bo2 = c.from_ice(dto)
