import math
import numpy as np

from armarx_core import ice_manager

from visionx import StereoCalibrationInterfacePrx
from visionx import ImageProviderInterfacePrx
from visionx import MonocularCalibration

from typing import Dict

import logging


logger = logging.getLogger(__name__)


def build_calibration_matrix(
    calibration: Dict[str, float], scale: float = None
) -> np.ndarray:
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
    fx = calibration["fx"]
    fy = calibration["fy"]
    cx = calibration.get("cx", None)
    cy = calibration.get("cy", None)
    if not cx:
        cx = calibration["width"] / 2.0
        cy = calibration["height"] / 2.0
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
    proxy = ImageProviderInterfacePrx.get_proxy(provider_name)
    image_format = proxy.getImageFormat()
    width = image_format.dimension.width
    height = image_format.dimension.height

    proxy = StereoCalibrationInterfacePrx.get_proxy(provider_name)
    frame = proxy.getReferenceFrame()
    stereo_calibration = proxy.getStereoCalibration()

    left_fx = stereo_calibration.calibrationLeft.cameraParam.focalLength[0]
    left_fy = stereo_calibration.calibrationLeft.cameraParam.focalLength[1]

    right_fx = stereo_calibration.calibrationRight.cameraParam.focalLength[0]
    right_fy = stereo_calibration.calibrationRight.cameraParam.focalLength[1]

    left_calibration = {
        "fx": left_fx,
        "fy": left_fy,
        "width": width,
        "height": height,
        "vertical_fov": 2.0 * math.atan(height / (2.0 * left_fy)),
        "horizontal_fov": 2.0 * math.atan(width / (2.0 * left_fx)),
    }

    right_calibration = {
        "fx": right_fx,
        "fy": right_fy,
        "width": width,
        "height": height,
        "vertical_fov": 2.0 * math.atan(height / (2.0 * right_fy)),
        "horizontal_fov": 2.0 * math.atan(width / (2.0 * right_fx)),
    }

    return {"left": left_calibration, "right": right_calibration, "frame": frame}


def get_armarx_stereo_calibration(provider_name: str):
    """
    Retrieves the camera calibration of an ArmarX ImageProvider via Ice.
    Calibration parameters are returned as dictionary of 'visionx.MonocularCalibration's.

    ..see:: image_to_world_coordinates() to convert points using this calibration

    :param provider_name: name of the component to connect to
    :returns: a dictionary of 'visionx.MonocularCalibration's
    """
    proxy = ice_manager.wait_for_proxy(StereoCalibrationInterfacePrx, provider_name)
    stereo_calibration = proxy.getStereoCalibration()
    return stereo_calibration


class MonocularCalibrationUtility(object):
    """
    Assumably faster version than using get_armarx_stereo_calibration() and image_to_world_coordinate() individually,
    as it stores certain results until the next call of image_to_world_coordinates.

    The image_to_world_coordinates() method does NOT yet take distortion parameters into account!
    Aside from that, the implementation follows <ivt/src/ivt/Calibration/Calibration.cpp>

    This visionx.camera_utils.MonocularCalibrationUtility class is different from visionx.MonocularCalibration, which
    is just a data type without business methods.
    """

    def __init__(
        self, provider_name: str, image_coordinates_are_normalized: bool = False
    ):
        """
        Retrieve the stereo calibration from the provider, check that left and right calibration are equal (monocular
        camera), and use the left one.

        :param provider_name: Name of the component that provides the stereo calibration
        """
        # store parameters
        self.stereo_calibration_provider_name = provider_name
        self.image_coordiantes_are_normalized = image_coordinates_are_normalized

        # initialization with neutral values
        self.calibration = None
        self.image_size_multiplier = np.ones(2)
        self.world_T_camera = np.identity(4)

        # actual initialization, incl. ice calls
        self._init_calibration()
        self._init_image_to_world_transformation()

    def _init_calibration(self):
        logger.debug(
            'Waiting for StereoCalibrationInterfaceProxy from component with name "{}"'.format(
                self.stereo_calibration_provider_name
            )
        )
        proxy = ice_manager.wait_for_proxy(
            StereoCalibrationInterfacePrx, self.stereo_calibration_provider_name
        )
        logger.debug("Retrieved StereoCalibrationInterfaceProxy")

        stereo_calibration = proxy.getStereoCalibration()
        if (
            not stereo_calibration.calibrationLeft
            == stereo_calibration.calibrationRight
        ):
            raise ValueError(
                "left and right calibration do not match, "
                "which violates the assumption of using a single RGBD camera"
            )
        self.calibration = stereo_calibration.calibrationLeft

    def _init_image_to_world_transformation(self):
        if self.image_coordiantes_are_normalized:
            self.image_size_multiplier = (
                self.calibration.cameraParam.width,
                self.calibration.cameraParam.height,
            )
        self.world_T_camera[0:3, 3] = np.array(self.calibration.cameraParam.translation)
        self.world_T_camera[0:3, 0:3] = np.array(self.calibration.cameraParam.rotation)

    def image_to_world_coordinates(self, image_Pt_point2D: np.ndarray, zc: float):
        camera_Pt_point_hom = np.zeros(4)
        world_Pt_point_hom = np.zeros(4)
        camera_Pt_point_hom[:2] = (
            (
                image_Pt_point2D * self.image_size_multiplier
                - self.calibration.cameraParam.principalPoint
            )
            / self.calibration.cameraParam.focalLength
            * zc
        )
        camera_Pt_point_hom[2] = zc

        world_Pt_point_hom = self.world_T_camera.dot(camera_Pt_point_hom)

        return world_Pt_point_hom[:3]


def image_to_world_coordinates(
    image_Pt_point: np.ndarray,
    zc: float,
    calibration: MonocularCalibration,
    image_coordinates_are_normalized: bool = False,
    world_T_camera: np.ndarray = None,
) -> np.ndarray:
    """
    Convert a point in an image to world coordinates.

    The method does NOT yet take distortion parameters into account!
    Aside from that, the implementation follows <ivt/src/ivt/Calibration/Calibration.cpp>

    :param image_Pt_point: 2D point in image frame
    :param zc: depth of the point in camera frame ('z camera')
    :param calibration: camera parameters
    :param world_T_camera: 4x4 homogenous matrix to transform the camera frame into the world frame
    :return: point in world frame
    """
    camera_Pt_point_hom = np.zeros(4)
    world_Pt_point_hom = np.zeros(4)

    x_multiplier = (
        calibration.cameraParam.width if image_coordinates_are_normalized else 1
    )
    y_multiplier = (
        calibration.cameraParam.height if image_coordinates_are_normalized else 1
    )

    camera_Pt_point_hom[0] = (
        (image_Pt_point[0] * x_multiplier - calibration.cameraParam.principalPoint[0])
        / calibration.cameraParam.focalLength[0]
        * zc
    )
    camera_Pt_point_hom[1] = (
        (image_Pt_point[1] * y_multiplier - calibration.cameraParam.principalPoint[1])
        / calibration.cameraParam.focalLength[1]
        * zc
    )
    camera_Pt_point_hom[2] = zc

    if world_T_camera is None:
        world_T_camera = np.identity(4)
        world_T_camera[0:3, 3] = np.array(calibration.cameraParam.translation)
        world_T_camera[0:3, 0:3] = np.array(calibration.cameraParam.rotation)

    world_Pt_point_hom = world_T_camera.dot(camera_Pt_point_hom)
    world_Pt_point = world_Pt_point_hom[:3]

    return world_Pt_point
