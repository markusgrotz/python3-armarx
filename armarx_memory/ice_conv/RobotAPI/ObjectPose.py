import numpy as np

from typing import Dict, Optional

from armarx_core import slice_loader

from armarx_memory.ice_conv.ice_twin import IceTwin
from armarx_memory.ice_conv.RobotAPI.Box import Box
from armarx_memory.ice_conv.RobotAPI.ObjectID import ObjectID
from armarx_memory.ice_conv.RobotAPI.PoseBase import PoseBaseConv


class ObjectPose(IceTwin):
    """
    A Python twin of `armarx.objpose.data.ObjectPose`
    from `objectpose/types.ice` in RobotAPI.
    """

    JointValues = Dict[str, float]

    def __init__(
        self,
        provider_name: str = "",
        object_id: ObjectID = None,
        object_pose_robot=None,
        object_pose_global=None,
        object_pose_original=None,
        object_pose_original_frame: str = "",
        robot_pose=None,
        local_oobb: Optional[Box] = None,
    ):
        self.provider_name = provider_name
        self.object_id = ObjectID() if object_id is None else object_id

        self.object_pose_robot = (
            np.eye(4) if object_pose_robot is None else np.array(object_pose_robot)
        )
        self.object_pose_global = (
            np.eye(4) if object_pose_global is None else np.array(object_pose_global)
        )
        self.object_pose_original = (
            np.eye(4)
            if object_pose_original is None
            else np.array(object_pose_original)
        )
        self.object_pose_original_frame = object_pose_original_frame

        self.object_joint_values: ObjectPose.JointValues = {}

        self.robot_pose = np.eye(4) if robot_pose is None else np.array(robot_pose)
        self.robot_config: ObjectPose.JointValues = {}

        # attachment

        self.confidence: float = 0.0
        self.timestamp_usec: int = -1

        self.local_oobb = local_oobb

        self.__pose_conv: Optional[PoseBaseConv] = None

    def get_aabb_robot(self):
        return self.local_oobb.to_aabb(self.object_pose_robot)

    def viz_oobb_robot(self, id: str, size_factor=1.0, **kwargs) -> "armarx.arviz.Box":
        import armarx.arviz as viz

        return viz.Box(
            id,
            pose=self.object_pose_robot @ self.local_oobb.pose,
            size=self.local_oobb.extents * size_factor,
            **kwargs,
        )

    @classmethod
    def _get_ice_cls(cls):
        slice_loader.load_armarx_slice("RobotAPI", "objectpose/object_pose_types.ice")
        from armarx.objpose.data import ObjectPose

        return ObjectPose

    def _set_from_ice(self, dto: "armarx.objpose.data.ObjectPose"):
        self.provider_name = dto.providerName
        self.object_id = ObjectID(dto.objectID)
        self.object_pose_robot = self._pose_conv.from_ice(dto.objectPoseRobot)
        self.object_pose_global = self._pose_conv.from_ice(dto.objectPoseGlobal)
        self.object_pose_original = self._pose_conv.from_ice(dto.objectPoseOriginal)
        self.object_pose_original_frame = dto.objectPoseOriginalFrame

        self.object_joint_values = dto.objectJointValues

        self.robot_config = dto.robotConfig
        self.robot_pose = self._pose_conv.from_ice(dto.robotPose)

        self.confidence = dto.confidence
        self.timestamp_usec = dto.timestamp.timeSinceEpoch.microSeconds

        if all(
            [dto.localOOBB.position, dto.localOOBB.orientation, dto.localOOBB.extents]
        ):
            self.local_oobb = Box.from_ice(dto.localOOBB)
        else:
            self.local_oobb = None

    def _set_to_ice(self, dto):
        dto.providerName = self.provider_name
        dto.objectID = self.object_id.to_ice()
        dto.objectPoseRobot = self._pose_conv.to_ice(self.object_pose_robot)
        dto.objectPoseGlobal = self._pose_conv.to_ice(self.object_pose_global)
        dto.objectPoseOriginal = self._pose_conv.to_ice(self.object_pose_original)
        dto.objectPoseOriginalFrame = self.object_pose_original_frame

        dto.objectJointValues = self.object_joint_values

        dto.robotConfig = self.robot_config
        dto.robotPose = self._pose_conv.to_ice(self.robot_pose)

        dto.confidence = self.confidence
        dto.timestamp.timeSinceEpoch.microSeconds = self.timestamp_usec

        if dto.localOOBB is not None and all(
            [dto.localOOBB.position, dto.localOOBB.orientation, dto.localOOBB.extents]
        ):
            dto.localOOBB = self.local_oobb.to_ice()
        else:
            dto.localOOBB = None

    @property
    def _pose_conv(self) -> PoseBaseConv:
        if self.__pose_conv is None:
            self.__pose_conv = PoseBaseConv()
        return self.__pose_conv

    def __repr__(self):
        return f"<{self.__class__.__name__} of {str(self.object_id)}>"
