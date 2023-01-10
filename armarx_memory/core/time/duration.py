import typing as ty


class Duration:

    def __init__(
            self,
            microseconds: int = 0,
    ):
        self._microseconds = microseconds

    def to_microseconds(self) -> int:
        return self._microseconds

    def __hash__(self) -> int:
        return hash(self._microseconds)

    def __eq__(self, other: "Duration") -> bool:
        return self._microseconds == other._microseconds

    def __ne__(self, other: "Duration") -> bool:
        return self._microseconds != other._microseconds

    def __lt__(self, other: "Duration") -> bool:
        return self._microseconds < other._microseconds

    def __le__(self, other: "Duration") -> bool:
        return self._microseconds <= other._microseconds

    def __gt__(self, other: "Duration") -> bool:
        return self._microseconds > other._microseconds

    def __ge__(self, other: "Duration") -> bool:
        return self._microseconds >= other._microseconds

    def __add__(self, other: "Duration") -> "Duration":
        return Duration(microseconds=self._microseconds + other._microseconds)

    # ToDo: Implement the other operators.
