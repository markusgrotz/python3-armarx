"""
This module provides functionality for receiving and providing point clouds in ArmarX.

Classes:
- PointCloudProvider: Can provide point clouds as numpy arrays.
- PointCloudReceiver: Can receive point clouds as numpy arrays.
"""

import logging
import threading

from typing import Tuple

import numpy as np

from armarx.ice_manager import register_object
from armarx.ice_manager import get_proxy
from armarx.ice_manager import using_topic


from visionx.pointcloud_provider import PointCloudProvider
from visionx.pointcloud_provider import dtype_from_point_type

from visionx import PointCloudProcessorInterfacePrx
from visionx import PointCloudProcessorInterface
from visionx import PointCloudProviderInterfacePrx
from visionx import PointCloudProviderInterface
from visionx import MetaPointCloudFormat
from visionx import PointContentType


logger = logging.getLogger(__name__)


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

