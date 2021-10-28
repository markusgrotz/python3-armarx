"""
This module provides functionality for receiving and providing point clouds in ArmarX.

Classes:
- PointCloudProvider: Can provide point clouds as numpy arrays.
- PointCloudReceiver: Can receive point clouds as numpy arrays.
"""

import logging
import threading
import time
from typing import Tuple


import numpy as np

from armarx.ice_manager import register_object, get_proxy, get_topic, using_topic
from armarx.slice_loader import _load_armarx_slice
_load_armarx_slice("VisionX", "core/PointCloudProcessorInterface.ice")

import visionx as vx

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


def dtype_from_point_type(point_type: vx.PointContentType):
    if point_type == vx.PointContentType.ePoints:
        return dtype_point_xyz
    if point_type == vx.PointContentType.eColoredPoints:
        return dtype_point_color_xyz
    if point_type == vx.PointContentType.eOrientedPoints:
        return dtype_point_normal_xyz
    if point_type == vx.PointContentType.eColoredOrientedPoints:
        return dtype_point_color_normal_xyz
    if point_type == vx.PointContentType.eLabeledPoints:
        return dtype_point_xyz_label
    if point_type == vx.PointContentType.eColoredLabeledPoints:
        return dtype_point_xyz_color_label
    if point_type == vx.PointContentType.eIntensity:
        return dtype_point_xyz_intensity
    raise Exception("PointContentType not yet implemented!", point_type)


def point_type_from_dtype(dt: np.dtype):
    if dt == dtype_point_xyz:
        return vx.PointContentType.ePoints
    if dt == dtype_point_color_xyz:
        return vx.PointContentType.eColoredPoints
    if dt == dtype_point_normal_xyz:
        return vx.PointContentType.eOrientedPoints
    if dt == dtype_point_color_normal_xyz:
        return vx.PointContentType.eColoredOrientedPoints
    if dt == dtype_point_xyz_label:
        return vx.PointContentType.eLabeledPoints
    if dt == dtype_point_xyz_color_label:
        return vx.PointContentType.eColoredLabeledPoints
    if dt == dtype_point_xyz_intensity:
        return vx.PointContentType.eIntensity
    raise Exception("Structured data type not known!", dt)


def get_point_cloud_format(max_points: int, point_dt: np.dtype) -> vx.MetaPointCloudFormat:
    result = vx.MetaPointCloudFormat()
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


class PointCloudProvider(vx.PointCloudProviderInterface):
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
        self.pc_topic = get_topic(vx.PointCloudProcessorInterfacePrx, f'{self.name}.PointCloudListener')

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


class PointCloudReceiver(vx.PointCloudProcessorInterface):
    """
    A point cloud receiver connects to a PointCloudProvider and makes reads new point cloud data if available.
    """

    def __init__(self, name: str,
                 source_provider_name: str = None,
                 connect: bool = False):
        """
        Constructs a point cloud reciever.

        A point cloud receiver connects to a source point cloud provider.
        It grants easy access to the source provider's point clouds as numpy arrays.

        :param name: Name of the receiver component
        :param source_provider_name: Name of the source point cloud provider (implements PointCloudProviderInterface)
        :param connect: Indicates whether the constructor should automatically connect, i.e. call on_connect()
        """
        self.name = name
        self.proxy = None

        self.cv = threading.Condition()
        self.point_cloud_available = False

        # Source provider is set in on_connect()
        self.source_provider_name = source_provider_name
        self.source_provider_proxy = None
        self.source_provider_topic = None
        self.source_format = None

        if connect:
            self.on_connect()

    def reportPointCloudAvailable(self, provider_name: str, current=None):
        with self.cv:
            self.point_cloud_available = True
            self.cv.notify()

    def wait_for_next_point_cloud(self) -> Tuple[np.array, vx.MetaPointCloudFormat]:
        """
        Wait for the next point cloud from the source provider to arrive, then return it.

        This function blocks until a new point cloud is provided.

        :return: Tuple consisting of received point cloud data and format
        """
        with self.cv:
            self.cv.wait_for(lambda: self.point_cloud_available)
            return self.get_latest_point_cloud()

    def get_latest_point_cloud(self) -> Tuple[np.array, vx.MetaPointCloudFormat]:
        """
        Get the latest point cloud without waiting.

        This function does not block but might return the same point cloud multiple times.

        :return: Tuple consisting of received point cloud data and format
        """
        raw_point_cloud, pc_format = self.source_provider_proxy.getPointCloud()
        # FIXME: Why can pc_format be not set here? It is an output parameter that should always be set.
        if pc_format is None:
            pc_format = self.source_format

        point_dtype = dtype_from_point_type(pc_format.type)
        point_cloud = np.frombuffer(raw_point_cloud, dtype=point_dtype)

        return point_cloud, pc_format

    def on_disconnect(self):
        """
        Call this function after you have finished receiving point clouds.
        """
        self.source_provider_topic.unsubscribe(self.proxy)

    def on_connect(self):
        """
        This function starts the connection with the source provider.

        After calling this function, wait_for_next_point_cloud() and get_latest_point_cloud() can be called.
        """
        logger.debug('Registering point cloud processor')
        self.proxy = register_object(self, self.name)
        self.source_provider_proxy = get_proxy(vx.PointCloudProviderInterfacePrx, self.source_provider_name)
        self.source_format = self.source_provider_proxy.getPointCloudFormat()

        self.source_provider_topic = using_topic(self.proxy, f'{self.source_provider_name}.PointCloudListener')

