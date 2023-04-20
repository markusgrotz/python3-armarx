import dataclasses as dc
import numpy as np

from armarx_memory.aron.aron_dataclass import AronDataclass


@dc.dataclass
class FrameID(AronDataclass):
    """
    Python implementation of `armarx::arondto::FrameID`
    defined in `RobotAPI/libraries/aron/common/aron/framed.xml`.
    """
    frame: str = ""
    agent: str = ""


@dc.dataclass
class FramedPosition(AronDataclass):
    """
    Python implementation of `armarx::arondto::FramedPosition`
    defined in `RobotAPI/libraries/aron/common/aron/framed.xml`.
    """
    header: FrameID = dc.field(default_factory=FrameID)
    position: np.ndarray = dc.field(default_factory=lambda: np.zeros(3, dtype=np.float32))


@dc.dataclass
class FramedOrientation(AronDataclass):
    """
    Python implementation of `armarx::arondto::FramedOrientation`
    defined in `RobotAPI/libraries/aron/common/aron/framed.xml`.
    """
    header: FrameID = dc.field(default_factory=FrameID)
    orientation: np.ndarray = dc.field(default_factory=lambda: np.array([1., 0., 0., 0.]))


@dc.dataclass
class FramedPose(AronDataclass):
    """
    Python implementation of `armarx::arondto::FramedOrientation`
    defined in `RobotAPI/libraries/aron/common/aron/framed.xml`.
    """
    header: FrameID = dc.field(default_factory=FrameID)
    pose: np.ndarray = dc.field(default_factory=lambda: np.eye(4, dtype=np.float32))
