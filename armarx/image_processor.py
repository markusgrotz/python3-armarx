import logging

from .ice_manager import using_topic
from .ice_manager import get_proxy
from .ice_manager import register_object
from .ice_manager import ice_communicator

from .image_provider import ImageProvider

from visionx import ImageProviderInterfacePrx
from visionx import ImageProcessorInterface

import numpy as np
import threading


logger = logging.getLogger(__name__)


class ImageProcessor(ImageProcessorInterface):

    def __init__(self, provider_name, num_result_images=None):
        super().__init__()
        self.provider_name = provider_name
        self.num_result_images = num_result_images

        self._thread = threading.Thread(target=self._process)
        self.image_available = False
        self.cv = threading.Condition()

    def reportImageAvailable(self, provider_name, current=None):
        with self.cv:
            self.image_available = True
            self.cv.notify()

    def _process(self):
        image_format = self.image_source.getImageFormat()
        number_of_images = self.image_source.getNumberImages()
        logger.debug('image format {}'.format(image_format))
        data_dimensions = (number_of_images, image_format.dimension.height, image_format.dimension.width, image_format.bytesPerPixel)
        logger.debug('data dimensions {}'.format(data_dimensions))

        while not ice_communicator.isShutdown():
            with self.cv:
                self.cv.wait_for(lambda: self.image_available)

                image_buffer = self.image_source.getImages()
                input_images = np.frombuffer(image_buffer, dtype=np.uint8).reshape(data_dimensions)

                result_images = self.process_image(input_images)
                self.result_image_provider.update_image(result_images)

    def process_image(self, images):
        pass

    def shutdown(self):
        self._image_listener_topic.unsubscribe(self._proxy)

    def register(self):
        logger.debug('Registering image processor')
        self._proxy = register_object(self, self.__class__.__name__)
        self.image_source = get_proxy(ImageProviderInterfacePrx, self.provider_name)

        d = self.image_source.getImageFormat().dimension
        if self.num_result_images is None:
            self.num_result_images = self.image_source.getNumberImages()
        self.result_image_provider = ImageProvider(self.__class__.__name__ + 'Result', self.num_result_images, d.width, d.height)
        self.result_image_provider.register()
        self._thread.start()
        self._image_listener_topic = using_topic(self._proxy, self.provider_name + '.ImageListener')
