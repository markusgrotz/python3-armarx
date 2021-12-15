import logging

import numpy as np

from visionx import ImageProviderInterfacePrx
from armarx.ice_manager import get_proxy

logger = logging.getLogger(__name__)


def read_images(provider_name: str = None) -> np.ndarray:
    provider_name = provider_name or 'OpenNIPointCloudProvider'

    image_provider = get_proxy(ImageProviderInterfacePrx, provider_name)

    image_format = image_provider.getImageFormat()
    number_of_images = image_provider.getNumberImages()
    data_dimensions = (number_of_images, image_format.dimension.height,
                       image_format.dimension.width, image_format.bytesPerPixel)

    image_buffer, info = image_provider.getImagesAndMetaInfo()
    input_images = np.frombuffer(image_buffer, dtype=np.uint8).reshape(data_dimensions)   

    return input_images

