import numpy as np
from visionx import ImageProviderInterfacePrx


def visualize_pose(img: np.ndarray, pose: np.ndarray, K: np.ndarray) -> np.ndarray:
    """
    Draws a 6-D pose as coordinate system on a given 2D color image.

    :param img: the input image
    :param pose: the pose to visualize
    :param K: the instric camera parameter
    :returns: the input image with the visualized pose
    """
    import cv2

    axis_length = 100
    axis_thickness = 3
    R = pose[:3, :3]
    t = pose[:3, 3]
    rot_vec, _ = cv2.Rodrigues(R)

    points = np.identity(3) * 100
    points = np.vstack([points, np.zeros((1, 3))])

    points = np.float32([[100, 0, 0], [0, 100, 0], [0, 0, 100], [0, 0, 0]]).reshape(
        -1, 3
    )

    axis_points, _ = cv2.projectPoints(points, rot_vec, t, K, (0, 0, 0, 0))
    img = cv2.line(
        img,
        tuple(axis_points[3].ravel()),
        tuple(axis_points[0].ravel()),
        (255, 0, 0),
        3,
    )
    img = cv2.line(
        img,
        tuple(axis_points[3].ravel()),
        tuple(axis_points[1].ravel()),
        (0, 255, 0),
        3,
    )
    img = cv2.line(
        img,
        tuple(axis_points[3].ravel()),
        tuple(axis_points[2].ravel()),
        (0, 0, 255),
        3,
    )

    return img


def convert_armarx_to_depth(image: np.ndarray) -> np.ndarray:
    if image.dtype == np.uint8 and image.shape[-1] == 3:
        depth = image[:, :, 0].astype(np.uint16)
        depth += np.left_shift(image[:, :, 1].astype(np.uint16), 8)
        return depth
    logger.warning("Invalid image type")
    return None


def convert_depth_to_armarx(depth: np.ndarray) -> np.ndarray:
    if depth.dtype == np.uint16 and depth.shape[-1] == 1:
        image = np.zeros((*depth.shape[:-1], 3), dtype=np.uint8)
        # ..todo:: modulo
        image[:, :, 0] = depth[:, :]
        image[:, :, 1] = np.right_shift(depth[:, :], 8)
        return image
    logger.warning("Invalid image type")
    return None


def read_images(provider_name: str = None) -> np.ndarray:
    provider_name = provider_name or "OpenNIPointCloudProvider"

    image_provider = ImageProviderInterfacePrx.get_proxy(provider_name)

    if not image_provider:
        return None

    image_format = image_provider.getImageFormat()
    number_of_images = image_provider.getNumberImages()
    data_dimensions = (
        number_of_images,
        image_format.dimension.height,
        image_format.dimension.width,
        image_format.bytesPerPixel,
    )

    image_buffer, info = image_provider.getImagesAndMetaInfo()
    input_images = np.frombuffer(image_buffer, dtype=np.uint8).reshape(data_dimensions)

    return input_images, info
