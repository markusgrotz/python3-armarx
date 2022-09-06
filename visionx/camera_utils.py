import math
import numpy as np

from armarx import ice_manager
from visionx import StereoCalibrationInterfacePrx
from visionx import ImageProviderInterfacePrx

from typing import Dict


def build_calibration_matrix(calibration: Dict[str, float], scale: float=None) -> np.ndarray:
    """
    Converts calibration parameters stored as a dictionary to a matrix with the
    intrinsic camera parameters.

    .. highlight:: python
    .. code-block:: python

        calibration = get_stereo_calibration('RCImageProvider')
        K = build_calibration_matrix(calibration['left'])

        import cv2
        points = np.float32([[100, 0, 0]])
        t = np.float32([0, 0, 0])
        rot_rec = np.float32([1, 0, 0])
        cv2.projectPoints(points, rot_vec, t, K, (0, 0, 0, 0))
        ...

    :param calibration: camera parameters
    :param scale: if the image is scaled
    :returns: the intrinsic camera parameters as matrix
    """
    fx = calibration['fx']
    fy = calibration['fy']
    cx = calibration.get('cx', None)
    cy = calibration.get('cy', None)
    if not cx:
        cx = calibration['width'] / 2.0
        cy = calibration['height'] / 2.0
    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
    if scale:
        K = K * scale
        K[2, 2] = 1
    return K


def get_stereo_calibration(provider_name: str):
    """
    Retrieves the camera calibration of an ArmarX ImageProvider via Ice.
    Calibration parameters are returned as dictionary.

    ..see:: build_calibration_matrix() to get a intrinsic calibration matrix

    :param provider_name: name of the component to connect to
    :returns: the calibration as dict
    """
    proxy = ice_manager.wait_for_proxy(ImageProviderInterfacePrx, provider_name)
    image_format = proxy.getImageFormat()
    width = image_format.dimension.width
    height = image_format.dimension.height

    proxy = ice_manager.wait_for_proxy(StereoCalibrationInterfacePrx, provider_name)
    frame = proxy.getReferenceFrame()
    stereo_calibration = proxy.getStereoCalibration()

    left_fx = stereo_calibration.calibrationLeft.cameraParam.focalLength[0]
    left_fy = stereo_calibration.calibrationLeft.cameraParam.focalLength[1]

    right_fx = stereo_calibration.calibrationRight.cameraParam.focalLength[0]
    right_fy = stereo_calibration.calibrationRight.cameraParam.focalLength[1]


    left_calibration = {'fx': left_fx, 'fy': left_fy, 'width': width, 'height': height,
                        'vertical_fov': 2.0 * math.atan(height / (2.0 * left_fy)),
                        'horizontal_fov': 2.0 * math.atan(width / (2.0 * left_fx))}

    right_calibration = {'fx': right_fx, 'fy': right_fy, 'width': width, 'height': height,
                         'vertical_fov': 2.0 * math.atan(height / (2.0 * right_fy)),
                         'horizontal_fov': 2.0 * math.atan(width / (2.0 * right_fx))}

    return {'left': left_calibration, 'right': right_calibration, 'frame': frame}
