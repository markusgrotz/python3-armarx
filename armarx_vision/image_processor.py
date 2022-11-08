import logging
import threading
import warnings

from abc import ABC
from abc import abstractmethod

from typing import Tuple
from typing import Any
from typing import Union

import numpy as np

from armarx_core.ice_manager import using_topic
from armarx_core.ice_manager import get_proxy
from armarx_core.ice_manager import register_object
from armarx_core.ice_manager import is_alive

from visionx.image_provider import ImageProvider

from visionx import ImageProviderInterfacePrx
from visionx import ImageProcessorInterface

from armarx import MetaInfoSizeBase

from .shm_tools import path_to_shm
from .shm_tools import read_images_shm


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

        self.shm_path = None

    def reportImageAvailable(self, provider_name, current=None):
        with self.cv:
            self.image_available = True
            self.cv.notify()

    def _get_images_and_info(self):
        if self.shm_path:
            info = MetaInfoSizeBase()  # self.image_source.getMetaInfo()
            images = read_images_shm(self.shm_path, self.data_dimensions)
        else:
            image_buffer, info = self.image_source.getImagesAndMetaInfo()
            images = np.frombuffer(image_buffer, dtype=np.uint8).reshape(
                self.data_dimensions
            )
        return images, info

    def _process(self):
        while is_alive():
            with self.cv:
                self.cv.wait_for(lambda: self.image_available)

                input_images, info = self._get_images_and_info()

                if hasattr(self, "process_image") and callable(self.process_image):
                    warnings.warn(
                        "Replaced with process_image(images, info)", DeprecationWarning
                    )
                    result = self.process_image(input_images)
                else:
                    result = self.process_images(input_images, info)

                if not result:
                    logger.warning("Unable to get images")
                    return
                elif isinstance(result, tuple):
                    result_images, info = result
                else:
                    result_images = result
                    info.timeProvided = 0

                self.result_image_provider.update_image(
                    result_images, info.timeProvided
                )

    @abstractmethod
    def process_images(
        self, images: np.ndarray, info: MetaInfoSizeBase
    ) -> Union[np.ndarray, Tuple[np.ndarray, MetaInfoSizeBase]]:
        """
        This function is called everytime a new image is available.
        Results are automatically published.

        :param images: the new images
        :param info: meta information about the image
        :returns: Either the result images only or a tuple containing the result image and the info
        """
        pass

    def register(self):
        warnings.warn("Replaced with on_connect", DeprecationWarning)
        self.on_connect()

    def shutdown(self):
        warnings.warn("Replaced with on_disconnect", DeprecationWarning)
        self.on_disconnect()

    def on_disconnect(self):
        self._image_listener_topic.unsubscribe(self._proxy)

    def on_connect(self):
        logger.debug("Registering image processor")
        proxy = register_object(self, self.__class__.__name__)
        self.image_source = get_proxy(ImageProviderInterfacePrx, self.provider_name)
        self.shm_path = path_to_shm(self.provider_name)

        number_of_images = self.image_source.getNumberImages()
        image_format = self.image_source.getImageFormat()
        d = image_format.dimension
        if self.num_result_images is None:
            self.num_result_images = self.image_source.getNumberImages()
        self.result_image_provider = ImageProvider(
            f"{self.__class__.__name__}Result",
            self.num_result_images,
            d.width,
            d.height,
        )
        self.result_image_provider.register()

        self.data_dimensions = (
            number_of_images,
            image_format.dimension.height,
            image_format.dimension.width,
            image_format.bytesPerPixel,
        )
        logger.debug("data dimensions %s", self.data_dimensions)

        self._thread.start()
        self._image_listener_topic = using_topic(
            proxy, f"{self.provider_name}.ImageListener"
        )
