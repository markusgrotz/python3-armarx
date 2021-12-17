import numpy as np

from typing import Union, List


def spherical2cartesian(
        polar: Union[List, np.ndarray],
        ) -> np.ndarray:

    polar = np.array(polar)
    assert polar.shape[-1] == 3
    radius = polar[..., 0]
    azim = polar[..., 1]
    elev = polar[..., 2]
    inclination = np.pi/2 - elev
    sin_inclination = np.sin(inclination)

    cartesian = polar.astype(np.float).copy()
    cartesian[..., 0] = radius * sin_inclination * np.cos(azim)  # x
    cartesian[..., 1] = radius * sin_inclination * np.sin(azim)  # y
    cartesian[..., 2] = radius * np.cos(inclination)  # z
    return cartesian


def cartesian2spherical(
        cartesian: Union[List, np.ndarray],
        ) -> np.ndarray:

    cartesian = np.array(cartesian)
    assert cartesian.shape[-1] == 3
    x = cartesian[..., 0]
    y = cartesian[..., 1]
    z = cartesian[..., 2]

    radius = np.linalg.norm(cartesian, axis=-1)  # radius
    azim = np.arctan2(y, x)  # angle phi
    inclination = np.arccos(z / radius)  # angle theta
    elev = np.pi/2 - inclination

    polar = cartesian.astype(np.float).copy()
    polar[..., 0] = radius
    polar[..., 1] = azim
    polar[..., 2] = elev
    return polar
