from typing import List, Union, Tuple, Any

import numpy as np

from armarx import slice_loader

slice_loader.load_armarx_slice("RobotAPI", "ArViz/Elements.ice")

import armarx
import armarx.viz as viz


def vector3f_to_numpy(v: armarx.Vector3f):
    return np.array([v.e0, v.e1, v.e2])

def vector3f_from_numpy(a: np.ndarray):
    return armarx.Vector3f(*map(float, a))


def vector3fs_to_numpy(vs: List[armarx.Vector3f]):
    return np.array([]) if len(vs) == 0 else np.stack(list(map(vector3f_to_numpy, vs)))

def vector3fs_from_numpy(array: np.ndarray):
    return list(map(vector3f_from_numpy, array))


def color_to_numpy(c: viz.data.Color) -> np.ndarray:
    return np.array([c.r, c.g, c.b, c.a])

def set_viz_color(c: viz.data.Color, value):
    if len(value) == 3:
        c.r, c.g, c.b = map(int, value)
        c.a = int(c.a)
    else:
        c.r, c.g, c.b, c.a = map(int, value)

def to_viz_color(value) -> viz.data.Color:
    c = viz.data.Color()
    set_viz_color(c, value)
    return c


def colored_point_to_numpy_full(point: viz.data.ColoredPoint):
    return np.array([point.x, point.y, point.z,
                     point.color.r, point.color.g, point.color.b, point.color.a])

def colored_point_to_numpy_position(point: viz.data.ColoredPoint):
    return np.array([point.x, point.y, point.z])

def colored_point_to_numpy_color(point: viz.data.ColoredPoint):
    return np.array([point.color.r, point.color.g, point.color.b, point.color.a])


def colored_points_to_numpy_full(points: List[viz.data.ColoredPoint]):
    if len(points) > 0:
        return np.stack(list(map(colored_point_to_numpy_full, points)))
    else:
        return np.array([])

def colored_points_to_numpy_positions(points: List[viz.data.ColoredPoint]):
    return np.stack(list(map(colored_point_to_numpy_position, points)))

def colored_points_to_numpy_colors(points: List[viz.data.ColoredPoint]):
    return np.stack(list(map(colored_point_to_numpy_color, points)))


def set_colored_point_from_numpy_position(cp: viz.data.ColoredPoint, pos: np.ndarray):
    pos = np.array(pos)
    cp.x, cp.y, cp.z = map(float, pos)


def set_colored_point_from_numpy(cp: viz.data.ColoredPoint, array: np.ndarray):
    array = np.array(array)
    if array.ndim != 1:
        raise ValueError("Trying to set colored point from non-flat array with shape {}.\nPassed: {}"
                         .format(array.shape, array))
    if len(array) not in [3, 6, 7]:
        raise ValueError("Trying to set colored point with {} elements (expected 3, 6, or 7).\nPassed: {}"
                         .format(len(array), array))

    if len(array) == 3:
        set_colored_point_from_numpy_position(cp, array)
    elif len(array) in [6, 7]:
        set_colored_point_from_numpy_position(cp, array[:3])
        set_viz_color(cp.color, array[3:])


def set_colored_points_from_numpy(cps: List[viz.data.ColoredPoint], array: np.ndarray):
    array = np.array(array)

    if len(cps) < len(array):
        cps += [viz.data.ColoredPoint() for _ in range(len(array) - len(cps))]
    elif len(cps) > len(array):
        del cps[len(array):]
    assert len(cps) == len(array)

    for cp, a in zip(cps, array):
        set_colored_point_from_numpy(cp, a)


def colored_point_from_numpy(point: np.ndarray):
    cp = viz.data.ColoredPoint()
    set_colored_point_from_numpy(cp, point)
    return cp


def colored_points_from_numpy(points: np.ndarray):
    return [colored_point_from_numpy(p) for p in points]
