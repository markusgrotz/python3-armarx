import logging
import threading
import warnings

from abc import ABC
from abc import abstractmethod

from typing import Tuple
from typing import Any
from typing import Union

from .ice_manager import using_topic
from .ice_manager import get_proxy
from .ice_manager import register_object
from .ice_manager import ice_communicator

from .image_provider import ImageProvider

from visionx import ImageProviderInterfacePrx
from visionx import ImageProcessorInterface

from armarx import MetaInfoSizeBase

import numpy as np

logger = logging.getLogger(__name__)

class ImageProcessor(ImageProcessorInterface, ABC):
    """
    An abstract class  to process images

    .. highlight:: python
    .. code-block:: python

        class TestImageProcessor(ImageProcessor):

            def process_images(self, images, info):
                info.timestamp = time.time()
                return np.random.random(images.shape) * 128, info


    """

    def __init__(self, provider_name: str, num_result_images: int = None):
        super().__init__()
        self.provider_name = provider_name
        self.num_result_images = num_result_images

        self._thread = threading.Thread(target=self._process)
        self.image_available = False
        self.cv = threading.Condition()

        self.image_source = None
        self.result_image_provider = None


    def reportImageAvailable(self, provider_name, current=None):
        with self.cv:
            self.image_available = True
            self.cv.notify()

    def _process(self):
        image_format = self.image_source.getImageFormat()
        number_of_images = self.image_source.getNumberImages()
        logger.debug('image format %s', image_format)
        data_dimensions = (number_of_images, image_format.dimension.height,
                           image_format.dimension.width, image_format.bytesPerPixel)
        logger.debug('data dimensions %s', data_dimensions)

        while not ice_communicator.isShutdown():
            with self.cv:
                self.cv.wait_for(lambda: self.image_available)

                image_buffer, info = self.image_source.getImagesAndMetaInfo()
                input_images = np.frombuffer(image_buffer, dtype=np.uint8).reshape(data_dimensions)

                if hasattr(self, 'process_image') and callable(self.process_image):
                    warnings.warn('Replaced with process_image(images, info)', DeprecationWarning)
                    result = self.process_image(self, input_images)
                else:
                    result = self.process_images(input_images, info)

                if isinstance(result, tuple):
                    result_images, info = result
                else:
                    result_images = result
                    info.timeProvided = 0

                self.result_image_provider.update_image(result_images, info.timeProvided)


    @abstractmethod
    def process_images(self, images: np.ndarray, info: MetaInfoSizeBase) -> Union[np.ndarray, Tuple[np.ndarray, MetaInfoSizeBase]]: 
        """
        This function is called everytime a new image is available.
        Results are automatically published.

        :param images: the new images
        :param info: meta information about the image
        :returns: Either the result images only or a tuple containing the result image and the info
        """
        pass

    def register(self):
        warnings.warn('Replaced with on_connect', DeprecationWarning)
        self.on_connect()

    def shutdown(self):
        warnings.warn('Replaced with on_disconnect', DeprecationWarning)
        self.on_disconnect()

    def on_disconnect(self):
        self._image_listener_topic.unsubscribe(self._proxy)

    def on_connect(self):
        logger.debug('Registering image processor')
        proxy = register_object(self, self.__class__.__name__)
        self.image_source = get_proxy(ImageProviderInterfacePrx, self.provider_name)

        d = self.image_source.getImageFormat().dimension
        if self.num_result_images is None:
            self.num_result_images = self.image_source.getNumberImages()
        self.result_image_provider = ImageProvider(f'{self.__class__.__name__}Result', self.num_result_images, d.width, d.height)
        self.result_image_provider.register()
        self._thread.start()
        self._image_listener_topic = using_topic(proxy, f'{self.provider_name}.ImageListener')
