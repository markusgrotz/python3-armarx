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

from armarx.ice_manager import register_object
from armarx.ice_manager import get_proxy
from armarx.ice_manager import get_topic
from armarx.ice_manager import using_topic

from visionx import PointCloudProviderInterfacePrx
from visionx import PointCloudProviderInterface
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


class PointCloudReceiver(PointCloudProcessorInterface):
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

    def wait_for_next_point_cloud(self) -> Tuple[np.array, MetaPointCloudFormat]:
        """
        Wait for the next point cloud from the source provider to arrive, then return it.

        This function blocks until a new point cloud is provided.

        :return: Tuple consisting of received point cloud data and format
        """
        with self.cv:
            self.cv.wait_for(lambda: self.point_cloud_available)
            return self.get_latest_point_cloud()

    def get_latest_point_cloud(self) -> Tuple[np.array, MetaPointCloudFormat]:
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
        self.source_provider_proxy = get_proxy(PointCloudProviderInterfacePrx, self.source_provider_name)
        self.source_format = self.source_provider_proxy.getPointCloudFormat()

        self.source_provider_topic = using_topic(self.proxy, f'{self.source_provider_name}.PointCloudListener')
