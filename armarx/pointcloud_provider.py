import logging
import numpy as np

from .ice_manager import register_object
from .ice_manager import get_topic
from .slice_loader import load_armarx_slice
load_armarx_slice('VisionX', 'core/PointCloudProviderInterface.ice')
load_armarx_slice('VisionX', 'core/PointCloudProcessorInterface.ice')

from armarx import armarx_factories
from .data_types import *
armarx_factories.register()

from visionx import PointCloudProviderInterface
from visionx import PointCloudProcessorInterfacePrx
from visionx import MetaPointCloudFormat
from visionx import PointContentType

logger = logging.getLogger(__name__)

FORMAT_TO_DTYPE_DICT = {
    PointContentType.ePoints: Point3D,
    PointContentType.eColoredPoints: ColoredPoint3D,
    PointContentType.eOrientedPoints: Normal3D,
    PointContentType.eLabeledPoints: LabeledPoint3D,
    PointContentType.eColoredLabeledPoints: ColoredLabeledPoint3D,
    PointContentType.eIntensity: IntensityPoint3D
}


class PointCloudProvider(PointCloudProviderInterface):
    
    def __init__(self, name, width, height, format=None):
        super(PointCloudProvider, self).__init__()
        self.name = name
        self.data_dimensions = (height*width, 7)
        if format is None:
            self.pointcloud_format = self._get_default_pointcloud_format(width, height)
        else:
            self.pointcloud_format = format
        self.dtype = self.get_dtype_from_format(self.pointcloud_format) # needs to be changed if other pointcloud type is used
        self.pointcloud = np.zeros((height*width, 7), dtype=self.dtype)
        self.pointcloud_topic = None
        self.proxy = None

    @staticmethod
    def get_dtype_from_format(format):
        return FORMAT_TO_DTYPE_DICT[format.type]

    def _get_default_pointcloud_format(self, width, height):
        pc_format = MetaPointCloudFormat()
        pc_format.width = width
        pc_format.height = height
        pc_format.type = PointContentType.eColoredPoints
        # number of bytes in eColoredPoints = 4 bytes color (RGBA) + 12 bytes position (3 floats)
        sizeof_eColoredPoints = 16
        pc_format.capacity = width * width * sizeof_eColoredPoints
        pc_format.size = pc_format.capacity
        # TODO: sequence number; might need to be changed
        pc_format.seq = 0
        return pc_format

    def update_pointcloud(self, pointcloud):
        self.pointcloud = np.array(pointcloud, dtype=self.dtype)
        if self.pointcloud_topic:
            self.pointcloud_topic.reportPointCloudAvailable(self.name)
        else:
            logger.warn("not registered, call register() method")

    def register(self):
        self.proxy = register_object(self, self.name)
        self.pointcloud_topic = get_topic(PointCloudProcessorInterfacePrx,
                                          "{}.PointCloudListener".format(self.name))

    def getPointCloudFormat(self, current=None):
        logger.debug('getPointCloudFormat() {}'.format(self.pointcloud_format))
        return self.pointcloud_format

    def getPointCloud(self, current=None):
        logger.debug('getPointCloud()')
        assert self.pointcloud.dtype == self.dtype
        # assumes pointcloud to be a numpy array;
        # The Ice Interface specifies and out parameter (the format), which means we need to return
        # a tuple of the pointcloud and the format
        return (self.pointcloud.tobytes(), self.pointcloud_format)

    def hasSharedMemorySupport(self, current=None):
        return False


    def shutdown(self, current=None):
        # FIXME: This throws an error: AttributeError: 'NoneType' object has no attribute 'adapter'
        current.adapter.getCommunicator().shutdown()