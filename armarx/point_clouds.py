import logging
from abc import ABC
import time

import numpy as np

from armarx.ice_manager import register_object, get_topic
from armarx.slice_loader import _load_armarx_slice
_load_armarx_slice("VisionX", "core/PointCloudProcessorInterface.ice")

import visionx as vx
import armarx as ax

PointCloudProviderInterface = vx.PointCloudProviderInterface
PointCloudProcessorInterfacePrx = vx.PointCloudProcessorInterfacePrx
MetaPointCloudFormat = vx.MetaPointCloudFormat
PointContentType = vx.PointContentType
MetaInfoSizeBase = ax.MetaInfoSizeBase


logger = logging.getLogger(__name__)

# Structured data types for point types defined in VisionX
# These are binary compatible with the Blob data used by PointCloudProvider
dt_point_xyz = np.dtype([('position', np.float32, (3,))])
dt_point_color_xyz = np.dtype([('color', np.uint32), ('position', np.float32, (3,))])
dt_point_normal_xyz = np.dtype([('normal', np.float32, (3,)), ('position', np.float32, (3,))])
dt_point_color_normal_xyz = np.dtype([('color', np.uint32), ('normal', np.float32, (3,)), ('position', np.float32, (3,))])
dt_point_xyz_label = np.dtype([('position', np.float32, (3,)), ('label', np.int32)])
dt_point_xyz_color_label = np.dtype([('position', np.float32, (3,)), ('color', np.uint32), ('label', np.int32)])
dt_point_xyz_intensity = np.dtype([('position', np.float32, (3,)), ('intensity', np.float32)])


def dt_from_point_type(point_type: PointContentType):
    if point_type == PointContentType.ePoints:
        return dt_point_xyz
    if point_type == PointContentType.eColoredPoints:
        return dt_point_color_xyz
    if point_type == PointContentType.eOrientedPoints:
        return dt_point_normal_xyz
    if point_type == PointContentType.eColoredOrientedPoints:
        return dt_point_color_normal_xyz
    if point_type == PointContentType.eLabeledPoints:
        return dt_point_xyz_label
    if point_type == PointContentType.eColoredLabeledPoints:
        return dt_point_xyz_color_label
    if point_type == PointContentType.eIntensity:
        return dt_point_xyz_intensity
    raise Exception("PointContentType not yet implemented!", point_type)


def point_type_from_dt(dt: np.dtype):
    if dt == dt_point_xyz:
        return PointContentType.ePoints
    if dt == dt_point_color_xyz:
        return PointContentType.eColoredPoints
    if dt == dt_point_normal_xyz:
        return PointContentType.eOrientedPoints
    if dt == dt_point_color_normal_xyz:
        return PointContentType.eColoredOrientedPoints
    if dt == dt_point_xyz_label:
        return PointContentType.eLabeledPoints
    if dt == dt_point_xyz_color_label:
        return PointContentType.eColoredLabeledPoints
    if dt == dt_point_xyz_intensity:
        return PointContentType.eIntensity
    raise Exception("Structured data type not known!", dt)


def get_point_cloud_format(max_points: int, point_dt: np.dtype) -> MetaPointCloudFormat:
    result = MetaPointCloudFormat()
    result.size = max_points * point_dt.itemsize
    result.capacity = result.size
    result.timeProvided = 0
    result.width = max_points
    result.height = 1
    result.type = point_type_from_dt(point_dt)
    result.seq = 0
    return result


class PointCloudProvider(PointCloudProviderInterface, ABC):
    """
    A point cloud provider offers point clouds.

    A new point cloud can be provided by update_point_cloud(). The point cloud should be created as
    a numpy array with the respective structured data type that was specified in the constructor (point_dt).
    You can use the create_point_cloud_array() method to create a compatible numpy array.
    """

    def __init__(self, name: str, max_points: int,
                 point_dt: np.dtype = dt_point_color_xyz):
        super().__init__()
        self.name = name
        self.point_dt = point_dt
        self.format = get_point_cloud_format(max_points, point_dt)
        # The points array is pre-allocated.
        # When update_point_cloud is called, the new data is copied into this array.
        self.points = self.create_point_cloud_array(max_points)

        self.pc_topic = None
        self.proxy = None

    def create_point_cloud_array(self, shape):
        """
        Create a numpy array with compatible type to provide to update_point_cloud() later.

        :param shape: Shape of the array to be created.
        :return: np.array with the desired shape and compatible dtype.
        """
        return np.zeros(shape, self.point_dt)

    def on_connect(self):
        """
        Register the image provider.
        """
        logger.debug('registering point cloud provider %s', self.name)
        self.proxy = register_object(self, self.name)
        self.pc_topic = get_topic(PointCloudProcessorInterfacePrx, f'{self.name}.PointCloudListener')

    def update_point_cloud(self, points: np.ndarray, time_provided: int = 0):
        """
        Publish a new point cloud

        :param points: np.array of points with compatible dtype.
        :param time_provided: time stamp of the images. If zero the current time will be used
        """
        if points.dtype != self.point_dt:
            raise Exception("Array data type is not compatible!", points.dtype, self.point_dt)

        # Do we need to guard this with a mutex? Probably...
        np.copyto(self.points, points)
        # format.size expects number of bytes (a point is np.float32 is 4 bytes)
        number_of_points = points.shape[0]
        new_size = number_of_points * points.dtype.itemsize

        self.format.size = new_size
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

    def shutdown(self, current=None):
        current.adapter.getCommunicator().shutdown()
