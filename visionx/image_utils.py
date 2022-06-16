import numpy as np
from visionx import ImageProviderInterfacePrx


def convert_armarx_to_depth(image: np.ndarray) -> np.ndarray:
    if image.dtype == np.uint8 and image.shape[-1] == 3:
        depth = image[:, :, 0].astype(np.uint16)
        depth += np.left_shift(image[:, :, 1].astype(np.uint16), 8)
        return depth
    logger.warning('Invalid image type')
    return None


def convert_depth_to_armarx(depth: np.ndarray) -> np.ndarray:
    if depth.dtype == np.uint16 and depth.shape[-1] == 1:
        image = np.zeros((*depth.shape[:-1], 3), dtype=np.uint8)
        # ..todo:: modulo
        image[:, :, 0] = depth[:, :]
        image[:, :, 1] = np.right_shift(depth[:, :], 8)
        return image
    logger.warning('Invalid image type')
    return None



def read_images(provider_name: str = None) -> np.ndarray:
    provider_name = provider_name or 'OpenNIPointCloudProvider'

    image_provider = ImageProviderInterfacePrx.get_proxy(provider_name)

    if not image_provider:
        return None

    image_format = image_provider.getImageFormat()
    number_of_images = image_provider.getNumberImages()
    data_dimensions = (number_of_images, image_format.dimension.height,
                       image_format.dimension.width, image_format.bytesPerPixel)

    image_buffer, info = image_provider.getImagesAndMetaInfo()
    input_images = np.frombuffer(image_buffer, dtype=np.uint8).reshape(data_dimensions)   

    return input_images, info
