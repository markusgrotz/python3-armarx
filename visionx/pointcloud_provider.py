"""
This module provides functionality for receiving and providing point clouds in ArmarX.

Classes:
- PointCloudProvider: Can provide point clouds as numpy arrays.
"""

import logging
import time
from typing import Tuple


import numpy as np

from armarx.ice_manager import get_topic, register_object

from visionx import PointCloudProviderInterfacePrx
from visionx import PointCloudProviderInterface
from visionx import PointCloudProcessorInterfacePrx
from visionx import PointCloudProcessorInterface
from visionx import MetaPointCloudFormat
from visionx import PointContentType



logger = logging.getLogger(__name__)

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



class PointCloudProvider(PointCloudProviderInterface):
    """
    A point cloud provider offers point clouds.

    A new point cloud can be provided by update_point_cloud(). The point cloud should be created as
    a numpy array with the respective structured data type that was specified in the constructor (point_dt).
    You can use the create_point_cloud_array() method to create a compatible numpy array.
    """

    def __init__(self, name: str,
                 point_dtype: np.dtype = dtype_point_color_xyz,
                 initial_capacity: int = 640*480,
                 connect: bool = False):
        super().__init__()
        self.name = name
        self.point_dtype = point_dtype
        self.format = get_point_cloud_format(initial_capacity, point_dtype)
        # The points array is pre-allocated.
        # When update_point_cloud is called, the new data is copied into this array.
        self.points = self.create_point_cloud_array(initial_capacity)

        self.pc_topic = None
        self.proxy = None

        if connect:
            self.on_connect()

    def create_point_cloud_array(self, shape):
        """
        Create a numpy array with compatible type to provide to update_point_cloud() later.

        :param shape: Shape of the array to be created.
        :return: np.array with the desired shape and compatible dtype.
        """
        return np.zeros(shape, self.point_dtype)

    def on_connect(self):
        """
        Register the point cloud provider in Ice.

        Call this function before calling update_point_cloud().
        """
        logger.debug('registering point cloud provider %s', self.name)
        self.proxy = register_object(self, self.name)
        self.pc_topic = get_topic(PointCloudProcessorInterfacePrx, f'{self.name}.PointCloudListener')

    def on_disconnect(self):
        """
        Currently not implemented, but might be used to cleanup after the provider is no longer needed.
        """
        # Does nothing currently
        pass

    def update_point_cloud(self, points: np.ndarray, time_provided: int = 0):
        """
        Publish a new point cloud

        :param points: np.array of points with compatible dtype.
        :param time_provided: time stamp of the images. If zero the current time will be used
        """
        if points.dtype != self.point_dtype:
            raise Exception("Array data type is not compatible!", points.dtype, self.point_dtype)

        # Do we need to guard this with a mutex? Probably...
        if points.shape[0] != self.points.shape[0]:
            self.points = np.copy(points)
        else:
            np.copyto(self.points, points)
        # format.size expects number of bytes (a point is np.float32 is 4 bytes)
        number_of_points = points.shape[0]
        new_size = number_of_points * points.dtype.itemsize

        self.format.size = new_size
        self.format.width = number_of_points
        self.format.timeProvided = time_provided or int(time.time() * 1000.0 * 1000.0)

        if self.pc_topic:
            self.pc_topic.reportPointCloudAvailable(self.name)
        else:
            logger.warning('not connected. call on_connect() method')

    def getPointCloudFormat(self, current=None):
        logger.debug('getPointCloudFormat() %s', self.format)
        return self.format

    def getPointCloud(self, current=None):
        logger.debug('getPointCloud() %s', self.format)
        return self.points, self.format

    def hasSharedMemorySupport(self, current=None):
        return False

