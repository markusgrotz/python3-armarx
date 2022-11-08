import logging
from abc import ABC
import time
import warnings

import numpy as np

from armarx_core.ice_manager import register_object
from armarx_core.ice_manager import get_topic

from visionx import ImageProcessorInterfacePrx
from visionx import ImageProviderInterface
from visionx import ImageFormatInfo
from visionx import ImageType
from armarx import MetaInfoSizeBase


logger = logging.getLogger(__name__)


class ImageProvider(ImageProviderInterface, ABC):
    """ """

    def __init__(
        self, name: str, num_images: int = 2, width: int = 640, height: int = 480
    ):
        super().__init__()
        self.name = name
        self.image_format = self._get_image_format(width, height)
        self.data_dimensions = (
            num_images,
            height,
            width,
            self.image_format.bytesPerPixel,
        )
        self.images = np.zeros(self.data_dimensions, dtype=np.uint8)
        image_size = self.image_format.bytesPerPixel * width * height
        self.info = MetaInfoSizeBase(image_size, image_size)

        self.image_topic = None
        self.proxy = None
        # self.register()

    def register(self):
        warnings.warn("Replaced with on_connect", DeprecationWarning)
        self.on_connect()

    def on_connect(self):
        """
        Register the image provider.
        """
        logger.debug("registering image processor %s", self.name)
        self.proxy = register_object(self, self.name)
        self.image_topic = get_topic(
            ImageProcessorInterfacePrx, f"{self.name}.ImageListener"
        )

    def update_image(self, images, time_provided=0):
        warnings.warn("Replaced with update_images", DeprecationWarning)
        self.update_images(images, time_provided)

    def update_images(self, images: np.ndarray, time_provided: int = 0):
        """
        Publish a new image

        :param images: the images to publish
        :param time_provided: time stamp of the images. If zero the current time will be used
        """
        self.images = images
        self.info.timeProvided = time_provided or int(time.time() * 1000.0 * 1000.0)
        if self.image_topic:
            self.image_topic.reportImageAvailable(self.name)
        else:
            logger.warning("not registered. call register() method")

    def _get_image_format(self, width, height):
        image_format = ImageFormatInfo()
        image_format.bytesPerPixel = 3
        image_format.dimension.width = width
        image_format.dimension.height = height
        image_format.type = ImageType.eRgb
        return image_format

    def getImageFormat(self, current=None):
        logger.debug("getImageFormat() %s", self.image_format)
        return self.image_format

    def getImagesAndMetaInfo(self, current=None):
        logger.debug("getImageFormat() %s", self.image_format)
        return memoryview(self.images), self.info

    def getImages(self, current=None):
        logger.debug("getImages()")
        return memoryview(self.images)

    def getNumberImages(self, current=None):
        return self.data_dimensions[0]

    def hasSharedMemorySupport(self, current=None):
        return False

    def shutdown(self, current=None):
        current.adapter.getCommunicator().shutdown()
