import logging

from .ice_manager import using_topic
from .ice_manager import get_proxy
from .ice_manager import register_object
from .ice_manager import ice_communicator

from .pointcloud_provider import PointCloudProvider
from .data_types import Point3D, ColoredPoint3D
from visionx import PointCloudProviderInterfacePrx
from visionx import PointCloudProcessorInterface

import numpy as np
import threading

logger = logging.getLogger(__name__)


# TODO: The processor assumes that the result provider has the same dtype as the source provider.


class PointCloudProcessor(PointCloudProcessorInterface):

    def __init__(self, provider_name):
        super().__init__()
        self.provider_name = provider_name
        self.pointcloud_source = None  # call register() method
        self.pointcloud_available = False
        self.result_pointcloud_provider = None  # call register() method
        self.output_format = None # if this is set, the output provider will use this format, otherwise it will use
        # the format of the input provider

        self._thread = threading.Thread(target=self._process)
        self._pointcloud_listener_topic = None
        self._cv = threading.Condition()

    def reportPointCloudAvailable(self, provider_name, current=None):
        with self._cv:
            self.pointcloud_available = True
            self._cv.notify()

    def _process(self):
        # logger.debug('pointcloud format {}'.format(pointcloud_format))
        # # TODO: change if something else than x, y, z-Coordinates is used
        # data_dimensions = (pointcloud_format.height * pointcloud_format.width, 3)
        # logger.debug('data dimensions {}'.format(data_dimensions))

        while not ice_communicator.isShutdown():
            with self._cv:
                self._cv.wait_for(lambda: self.pointcloud_available)

                # pointcloud_buffer = self.pointcloud_source.getPointCloud(pointcloud_format)
                ice_return = self.pointcloud_source.getPointCloud()
                pointcloud_buffer = ice_return[0]
                pointcloud_format = ice_return[1]
                if pointcloud_format is not None:
                    dtype = PointCloudProvider.get_dtype_from_format(pointcloud_format)
                else:
                    dtype = ColoredPoint3D
                input_pointclouds = np.frombuffer(pointcloud_buffer, dtype=dtype)

                result_pointclouds = self.process_pointcloud(input_pointclouds)
                self.result_pointcloud_provider.update_pointcloud(result_pointclouds)

    def process_pointcloud(self, pointclouds):
        logger.warn("Calling abs method process_pointcloud()")
        return pointclouds

    def shutdown(self):
        self._pointcloud_listener_topic.unsubscribe(self._proxy)

    def register(self):
        logger.debug('Registering pointcloud processor')
        self._proxy = register_object(self, self.__class__.__name__)
        self.pointcloud_source = get_proxy(PointCloudProviderInterfacePrx, self.provider_name)
        if self.output_format is None:
            self.output_format = self.pointcloud_source.getPointCloudFormat()
        self.result_pointcloud_provider = PointCloudProvider(self.__class__.__name__ + 'Result',
                                                             self.output_format.width, self.output_format.height,
                                                             self.output_format)
        self.result_pointcloud_provider.register()
        self._thread.start()
        self._pointcloud_listener_topic = using_topic(self._proxy, self.provider_name + '.PointCloudListener')
