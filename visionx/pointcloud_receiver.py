"""
This module provides functionality for receiving point clouds in ArmarX.

Classes:
- PointCloudReceiver: Can receive point clouds as numpy arrays.
"""

import logging
import threading

import numpy as np

from typing import Tuple

from armarx_core import ice_manager

from visionx.pointclouds import dtype_from_point_type
from visionx.pointclouds import PointCloudProcessorInterface
from visionx.pointclouds import PointCloudProviderInterfacePrx
from visionx.pointclouds import MetaPointCloudFormat


logger = logging.getLogger(__name__)


class PointCloudReceiver(PointCloudProcessorInterface):
    """
    A point cloud receiver connects to a PointCloudProvider and makes reads new point cloud data if available.
    """

    def __init__(
        self,
        name: str,
        source_provider_name: str = None,
        connect: bool = False,
        wait_for_provider=True,
    ):
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

        self._wait_for_provider = wait_for_provider

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
        logger.debug("Registering point cloud processor")
        self.proxy = ice_manager.register_object(self, self.name)
        if self._wait_for_provider:
            self.source_provider_proxy = ice_manager.wait_for_proxy(
                PointCloudProviderInterfacePrx, self.source_provider_name
            )
        else:
            self.source_provider_proxy = ice_manager.get_proxy(
                PointCloudProviderInterfacePrx, self.source_provider_name
            )
        self.source_format = self.source_provider_proxy.getPointCloudFormat()

        self.source_provider_topic = ice_manager.using_topic(
            self.proxy, f"{self.source_provider_name}.PointCloudListener"
        )
