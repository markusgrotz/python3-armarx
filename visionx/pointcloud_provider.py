"""
This module provides functionality for providing point clouds in ArmarX.

Classes:
- PointCloudProvider: Can provide point clouds as numpy arrays.
"""

import logging
import time

import numpy as np

from armarx_core import ice_manager

from visionx.pointclouds import dtype_point_color_xyz, get_point_cloud_format
from visionx.pointclouds import (
    PointCloudProviderInterface,
    PointCloudProcessorInterfacePrx,
)


logger = logging.getLogger(__name__)


class PointCloudProvider(PointCloudProviderInterface):
    """
    A point cloud provider offers point clouds.

    A new point cloud can be provided by update_point_cloud(). The point cloud should be created as
    a numpy array with the respective structured data type that was specified in the constructor (point_dt).
    You can use the create_point_cloud_array() method to create a compatible numpy array.
    """

    def __init__(
        self,
        name: str,
        point_dtype: np.dtype = dtype_point_color_xyz,
        initial_capacity: int = 640 * 480,
        connect: bool = False,
    ):
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
        logger.debug("registering point cloud provider %s", self.name)
        self.proxy = ice_manager.register_object(self, self.name)
        self.pc_topic = ice_manager.get_topic(
            PointCloudProcessorInterfacePrx, f"{self.name}.PointCloudListener"
        )

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
            raise Exception(
                "Array data type is not compatible!", points.dtype, self.point_dtype
            )

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
            logger.warning("not connected. call on_connect() method")

    def getPointCloudFormat(self, current=None):
        logger.debug("getPointCloudFormat() %s", self.format)
        return self.format

    def getPointCloud(self, current=None):
        logger.debug("getPointCloud() %s", self.format)
        return self.points, self.format

    def hasSharedMemorySupport(self, current=None):
        return False
