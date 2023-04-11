import time


class Metronome:
    """
    A cycle clock allowing you to run a while-loop with an (approximately)
    fixed frequency.

    Example for 10 Hz:

    cycle = CycleClock(frequency_hertz=10)  # alternative: duration_seconds=0.01
    while True:
        ...  # Do stuff.

        cycle.wait_for_next_cycle()
    """

    def __init__(
        self,
        duration_seconds: float = None,
        frequency_hertz: float = None,
    ):
        self.duration_seconds: float
        if duration_seconds is not None:
            self.duration_seconds = duration_seconds

        elif frequency_hertz is not None:
            self.duration_seconds = 1 / frequency_hertz

        else:
            raise ValueError(
                "Either duration_seconds or frequency_hertz must be specified."
            )

        self.start: float = 0.0
        self.reset()

    def reset(self):
        self.start = time.time()

    @property
    def remaining_seconds(self) -> float:
        return self.duration_seconds - (time.time() - self.start)

    def wait_for_next_tick(self):
        remaining = self.remaining_seconds
        if remaining > 0:
            time.sleep(remaining)
        self.reset()
