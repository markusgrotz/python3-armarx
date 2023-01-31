import dataclasses as dc
import typing as ty

from armarx_memory.aron.aron_dataclass import AronDataclass
from armarx_memory.aron.common.framed import FramedPosition, FramedOrientation


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
