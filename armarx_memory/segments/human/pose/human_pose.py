import dataclasses as dc
import numpy as np
import typing as ty

from armarx_memory.aron.aron_dataclass import AronDataclass
from armarx_memory.aron.common.framed import FramedPosition, FramedOrientation
from armarx_memory import client as amc


@dc.dataclass
class PoseKeypoint(AronDataclass):
    """
    Python implementation of `armarx::human::arondto::PoseKeypoint`
    defined in `VisionX/libraries/armem_human/aron/HumanPose.xml`.
    """

    position_camera: FramedPosition = dc.field(default_factory=FramedPosition)
    orientation_camera: ty.Optional[FramedOrientation] = None

    position_robot: ty.Optional[FramedPosition] = None
    orientation_robot: ty.Optional[FramedOrientation] = None

    position_global: ty.Optional[FramedPosition] = None
    orientation_global: ty.Optional[FramedOrientation] = None

    confidence: float = 0.0

    @classmethod
    def _get_conversion_options(cls):
        from armarx_memory.aron.conversion import ConversionOptions
        return ConversionOptions(
            names_snake_case_to_camel_case=True,
        )


@dc.dataclass
class HumanPose(AronDataclass):
    """
    Python implementation of `armarx::human::arondto::HumanPose`
    defined in `VisionX/libraries/armem_human/aron/HumanPose.xml`.
    """

    pose_model_id: str = ""
    human_tracking_id: ty.Optional[str] = ""

    keypoints: ty.Dict[str, PoseKeypoint] = dc.field(default_factory=dict)

    @classmethod
    def _get_conversion_options(cls):
        from armarx_memory.aron.conversion import ConversionOptions
        return ConversionOptions(
            names_snake_case_to_camel_case=True,
        )

    def get_3d_bounding_box(self, frame="global") -> np.ndarray:
        """
        Compute the axis aligned bounding box of all keypoints in
        :param frame: One of "global", "robot", "camera".
        :return: The limits in a (2, 3) array, i.e.
            [[min_x, min_y, min_z], [max_x, max_y, max_z]]
        """
        minimum, maximum = None, None
        for name, keypoint in self.keypoints.items():

            framed_position = {
                "global": keypoint.position_camera,
                "robot": keypoint.position_robot,
                "camera": keypoint.position_camera,
            }[frame]

            position: np.ndarray = framed_position.position

            position = np.squeeze(position)
            assert position.shape == (3,), position.shape
            if minimum is None:
                assert maximum is None
                minimum = maximum = position
            else:
                minimum = np.min([minimum, position], axis=0)
                maximum = np.max([maximum, position], axis=0)

        return np.stack([minimum, maximum])


class HumanPoseReader:

    CORE_SEGMENT_ID = amc.MemoryID("Human", "Pose")

    def __init__(self, reader: amc.Reader):
        self.reader = reader

    @classmethod
    def from_mns(cls, mns: amc.MemoryNameSystem, wait=True) -> "HumanPoseReader":
        return cls(
            mns.wait_for_reader(cls.CORE_SEGMENT_ID)
            if wait
            else mns.get_reader(cls.CORE_SEGMENT_ID)
        )
