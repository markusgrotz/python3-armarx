import numpy as np


def rescale(value, from_lo, from_hi, to_lo, to_hi, clip=False):
    """
    Rescale a value from interval [from_lo, from_hi] to interval [to_lo, to_hi].
    :param clip: If true, the result is clipped to [to_lo, to_hi].
    :return: The rescaled value(s).
    """
    # value in [from_lo, from_hi]
    norm = (value - from_lo) / (from_hi - from_lo)  # [0, 1]
    scaled = norm * (to_hi - to_lo) + to_lo  # [to_lo, to_hi]
    if clip and to_lo > to_hi:
        to_lo, to_hi = to_hi, to_lo
    return scaled if not clip else np.clip(scaled, to_lo, to_hi)
