import logging
import numpy as np

from .ice_manager import register_object
from .ice_manager import get_topic
from .slice_loader import load_armarx_slice
load_armarx_slice('VisionX', 'core/ImageProviderInterface.ice')
load_armarx_slice('VisionX', 'core/ImageProcessorInterface.ice')
import time


from armarx import armarx_factories
armarx_factories.register()

from visionx import ImageProviderInterface
from visionx import ImageProcessorInterfacePrx
from visionx import ImageFormatInfo
from visionx import ImageType
from armarx import MetaInfoSizeBase


logger = logging.getLogger(__name__)


class ImageProvider(ImageProviderInterface):

    def __init__(self, name, num_images=2, width=640, height=480):
        super(ImageProviderInterface, self).__init__()
        self.name = name
        self.image_format = self._get_image_format(width, height)
        self.data_dimensions = (num_images, height, width, self.image_format.bytesPerPixel)
        self.images = np.zeros(self.data_dimensions, dtype=np.uint8)
        self.image_topic = None
        self.proxy = None

    def register(self):
        self.proxy = register_object(self, self.name)
        self.image_topic = get_topic(ImageProcessorInterfacePrx, '{}.ImageListener'.format(self.name))

    def update_image(self, images, time_provided = 0):
        self.images = images
        self.time_provided = time_provided or int(time.time() * 1000.0 * 1000.0)
        if self.image_topic:
            self.image_topic.reportImageAvailable(self.name)
        else:
            logger.warn('not registered. call register() method')

    def _get_image_format(self, width, height):
        image_format = ImageFormatInfo()
        image_format.bytesPerPixel = 3
        image_format.dimension.width = width
        image_format.dimension.height = height
        image_format.type = ImageType.eRgb
        return image_format

    def getImageFormat(self, current=None):
        logger.debug('getImageFormat() {}'.format(self.image_format))
        return self.image_format

    def getImagesAndMetaInfo(self,  current=None):
        logger.debug('getImageFormat() {}'.format(self.image_format))
        info = MetaInfoSizeBase()
        d = self.image_format.dimension
        info.size = self.image_format.bytesPerPixel * d.width *  d.height
        info.capacity = info.size
        info.timeProvided = self.time_provided
        return memoryview(self.images), info

    def getImages(self, current=None):
        logger.debug('getImages()')
        return memoryview(self.images)

    def getNumberImages(self, current=None):
        return self.data_dimensions[0]

    def hasSharedMemorySupport(self, current=None):
        return False

    def shutdown(self, current=None):
        current.adapter.getCommunicator().shutdown()
