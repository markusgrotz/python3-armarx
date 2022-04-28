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


def convert_armarx_to_depth(image: np.ndarray) -> np.ndarray:
    if image.dtype == np.uint8 and image.shape[-1] == 3:
        depth = np.zeros((*image.shape[:-1], 1)).astype(np.uint16)
        depth = image[:, :, 0] + np.left_shift(image[:, :, 1], 8)
        return depth
    logger.warning('Invalid image type')
    return None


def convert_depth_to_armarx(depth: np.ndarray) -> np.ndarray:
    if depth.dtype == np.uint16 and depth.shape[-1] == 1:
        image = np.zeros((*depth.shape[:-1], 1)).astype(np.uint8)
        image[:, :, 0] = depth[:, :]
        image[:, :, 1] = np.right_shift(depth[:, :], 8)
        return image
    logger.warning('Invalid image type')
    return None

   



