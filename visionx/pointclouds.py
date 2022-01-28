"""
This module provides functionality for receiving and providing point clouds in ArmarX.

Classes:
- PointCloudProvider: Can provide point clouds as numpy arrays.
"""

from typing import Tuple

import numpy as np

from visionx import PointCloudProviderInterfacePrx
from visionx import PointCloudProviderInterface
from visionx import PointCloudProcessorInterfacePrx
from visionx import PointCloudProcessorInterface
from visionx import MetaPointCloudFormat
from visionx import PointContentType



# Structured data types for point types defined in VisionX
# These are binary compatible with the Blob data used by PointCloudProvider
dtype_point_xyz = np.dtype([('position', np.float32, (3,))])
dtype_point_color_xyz = np.dtype([('color', np.uint32), ('position', np.float32, (3,))])
dtype_point_normal_xyz = np.dtype([('normal', np.float32, (3,)), ('position', np.float32, (3,))])
dtype_point_color_normal_xyz = np.dtype([('color', np.uint32), ('normal', np.float32, (3,)), ('position', np.float32, (3,))])
dtype_point_xyz_label = np.dtype([('position', np.float32, (3,)), ('label', np.int32)])
dtype_point_xyz_color_label = np.dtype([('position', np.float32, (3,)), ('color', np.uint32), ('label', np.int32)])
dtype_point_xyz_intensity = np.dtype([('position', np.float32, (3,)), ('intensity', np.float32)])


# Color as RGBA
dtype_point_rgba_xyz = np.dtype([
    ('r', np.uint8), ('g', np.uint8), ('b', np.uint8), ('a', np.uint8),
    ('position', np.float32, (3,))
])
dtype_point_rgba_normal_xyz = np.dtype([
    ('r', np.uint8), ('g', np.uint8), ('b', np.uint8), ('a', np.uint8),
    ('normal', np.float32, (3,)), ('position', np.float32, (3,))
])
dtype_point_xyz_rgba_label = np.dtype([
    ('position', np.float32, (3,)),
    ('r', np.uint8), ('g', np.uint8), ('b', np.uint8), ('a', np.uint8),
    ('label', np.int32)
])


dtype_color_to_rgba_dict = {
    dtype_point_color_xyz: dtype_point_rgba_xyz,
    dtype_point_color_normal_xyz: dtype_point_rgba_normal_xyz,
    dtype_point_xyz_color_label: dtype_point_xyz_rgba_label,
}
dtype_rgba_to_color_dict = {v: k for k, v in dtype_color_to_rgba_dict.items()}


def dtype_from_point_type(point_type: PointContentType):
    if point_type == PointContentType.ePoints:
        return dtype_point_xyz
    if point_type == PointContentType.eColoredPoints:
        return dtype_point_color_xyz
    if point_type == PointContentType.eOrientedPoints:
        return dtype_point_normal_xyz
    if point_type == PointContentType.eColoredOrientedPoints:
        return dtype_point_color_normal_xyz
    if point_type == PointContentType.eLabeledPoints:
        return dtype_point_xyz_label
    if point_type == PointContentType.eColoredLabeledPoints:
        return dtype_point_xyz_color_label
    if point_type == PointContentType.eIntensity:
        return dtype_point_xyz_intensity
    raise Exception("PointContentType not yet implemented!", point_type)


def point_type_from_dtype(dt: np.dtype):
    if dt == dtype_point_xyz:
        return PointContentType.ePoints
    if dt == dtype_point_color_xyz:
        return PointContentType.eColoredPoints
    if dt == dtype_point_normal_xyz:
        return PointContentType.eOrientedPoints
    if dt == dtype_point_color_normal_xyz:
        return PointContentType.eColoredOrientedPoints
    if dt == dtype_point_xyz_label:
        return PointContentType.eLabeledPoints
    if dt == dtype_point_xyz_color_label:
        return PointContentType.eColoredLabeledPoints
    if dt == dtype_point_xyz_intensity:
        return PointContentType.eIntensity
    raise Exception("Structured data type not known!", dt)


def get_point_cloud_format(max_points: int, point_dt: np.dtype) -> MetaPointCloudFormat:
    result = MetaPointCloudFormat()
    result.size = max_points * point_dt.itemsize
    result.capacity = result.size
    result.timeProvided = 0
    result.width = max_points
    result.height = 1
    result.type = point_type_from_dtype(point_dt)
    result.seq = 0
    return result


def rgb_to_uint32(r: int, g: int, b: int):
    r, g, b = [np.clip(c, 0, 255) for c in [r, g, b]]
    return r + g * 256 + b * 256 * 256


def uint32_to_rgb(color: int) -> Tuple[int, int, int]:
    r = color % 256
    color //= 256
    g = color % 256
    color //= 256
    b = color % 256
    return r, g, b


def uint32_to_rgb_array(color_array: np.ndarray) -> np.ndarray:
    rgba_dtype = dtype_color_to_rgba_dict[color_array.dtype]
    return color_array.view(rgba_dtype)


def rgb_to_uint32_array(rgba_array: np.ndarray) -> np.ndarray:
    color_dtype = dtype_rgba_to_color_dict[rgba_array.dtype]
    return rgba_array.view(color_dtype)


def crop_by_position(
        pc: np.ndarray,
        crop_min: Tuple[float, float, float],
        crop_max: Tuple[float, float, float],
) -> np.ndarray:
    from functools import reduce

    masks = [pc["position"][:, i] >= threshold for i, threshold in enumerate(crop_min)
             if threshold is not None]
    masks += [pc["position"][:, i] <= threshold for i, threshold in enumerate(crop_max)
              if threshold is not None]

    if len(masks) > 0:
        mask = reduce(np.logical_and, masks[1:], masks[0])
        return pc[mask]
    else:
        return pc

