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


def read_images(image_provider):
    image_format = image_provider.getImageFormat()
    logger.debug('image format {}'.format(image_format))

    number_of_images = image_provider.getNumberImages()
    data_dimensions = (number_of_images, image_format.dimension.height, image_format.dimension.width, image_format.bytesPerPixel)
    logger.debug('data dimensions {}'.format(data_dimensions))
    image_buffer = image_provider.getImages()
    images = np.frombuffer(image_buffer, dtype=np.uint8).reshape(data_dimensions)

    return images


class ImageProcessor(ImageProcessorInterface):

    def __init__(self, provider_name):
        super().__init__()
        self.provider_name = provider_name
        self.result_image_provider = ImageProvider(self.__class__.__name__ + 'Result')

        self.thread = threading.Thread(target=self.process)
        self.cv = threading.Condition()
        self.image_available = False

    def reportImageAvailable(self, provider_name, current=None):
        with self.cv:
            self.image_available = True
            self.cv.notify()

    def process(self):
        while not ice_communicator.isShutdown():
            with self.cv:
                self.cv.wait_for(lambda: self.image_available)
                images = read_images(self.image_source)
                images = self.process_image(images)
                self.result_image_provider.update_image(images)

    def process_image(self, images):
        pass

    def shutdown(self):
        self.image_listener_topic.unsubscribe(self)

    def register(self):
        logger.debug('Registering image processor')
        self.result_image_provider.register()
        self.proxy = register_object(self, self.__class__.__name__)
        self.image_source = get_proxy(ImageProviderInterfacePrx, self.provider_name)
        self.thread.start()
        self.image_listener_topic = using_topic(self.proxy, self.provider_name + '.ImageListener')
