import typing as ty

from armarx_memory.core.time.clock_type import ClockType
from armarx_memory.core.time.duration import Duration


class DateTime:

    INVALID_TIME_SINCE_EPOCH = Duration(microseconds=-9223372036854775808)

    def __init__(
            self,
            time_since_epoch: Duration = None,
            clock_type: ClockType = ClockType.Unknown,
            hostname: str = "unknown",
    ):
        self._time_since_epoch = time_since_epoch if time_since_epoch is not None else Duration()
        self._clock_type = clock_type
        self._hostname = hostname

    def __hash__(self) -> int:
        return hash(self._time_since_epoch)

    def __eq__(self, other: "DateTime") -> bool:
        return self._time_since_epoch == other._time_since_epoch

    def __ne__(self, other: "DateTime") -> bool:
        return self._time_since_epoch != other._time_since_epoch

    def __lt__(self, other: "DateTime") -> bool:
        return self._time_since_epoch < other._time_since_epoch

    def __le__(self, other: "DateTime") -> bool:
        return self._time_since_epoch <= other._time_since_epoch

    def __gt__(self, other: "DateTime") -> bool:
        return self._time_since_epoch > other._time_since_epoch

    def __ge__(self, other: "DateTime") -> bool:
        return self._time_since_epoch >= other._time_since_epoch

    # ToDo: Implement arithmetic operators.

    @property
    def time_since_epoch(self) -> Duration:
        return self._time_since_epoch

    @time_since_epoch.setter
    def time_since_epoch(self, value: Duration):
        self._time_since_epoch = value
