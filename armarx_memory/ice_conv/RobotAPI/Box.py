import numpy as np

from typing import Dict, List, Optional

from armarx_core import slice_loader

from armarx_memory.ice_conv.ice_twin import IceTwin
from armarx_memory.ice_conv.RobotAPI.PoseBase import Vector3BaseConv, QuaternionBaseConv


class Box(IceTwin):
    """
    A Python twin of the Ice DTO class `armarx.objpose.Box`
    from `objectpose/object_pose_types.ice` in RobotAPI.
    """

    def __init__(
        self,
        position: Optional[np.ndarray] = None,
        orientation: Optional[np.ndarray] = None,
        extents: Optional[np.ndarray] = None,
    ):
        import transforms3d as tf3d

        self.position = (
            np.array(position) if position is not None else np.zeros(3, dtype=float)
        )
        self.orientation = (
            np.array(orientation)
            if orientation is not None
            else tf3d.quaternions.qeye()
        )
        self.extents = (
            np.array(extents) if extents is not None else np.zeros(3, dtype=float)
        )

        self.__vec3_conv: Optional[Vector3BaseConv] = None
        self.__quat_conv: Optional[QuaternionBaseConv] = None

    @property
    def pose(self) -> np.ndarray:
        import transforms3d as tf3d

        return tf3d.affines.compose(
            T=self.position, R=tf3d.quaternions.quat2mat(self.orientation), Z=np.ones(3)
        )

    @classmethod
    def from_aabb(cls, minim, maxim) -> "Box":
        minim = np.array(minim)
        maxim = np.array(maxim)
        position = 0.5 * (minim + maxim)
        extents = maxim - minim
        return Box(position=position, extents=extents)

    @classmethod
    def from_aabb_dict(cls, aabb_dict: Dict) -> "Box":
        return cls.from_aabb(minim=aabb_dict["min"], maxim=aabb_dict["max"])

    def get_corners(self, global_pose=np.eye(4)) -> List[np.ndarray]:
        pose = global_pose @ self.pose
        pos = pose[:3, 3]
        ori = pose[:3, :3]
        points = []
        for ext, axis in zip(self.extents, ori.T):
            for s in [-1, 1]:
                points.append(pos + s * 0.5 * ext * axis)
        return points

    def to_aabb(self, global_pose=np.eye(4)):
        import transforms3d as tf3d

        points = np.array(self.get_corners(global_pose))

        pmin = np.min(points, axis=0)
        pmax = np.max(points, axis=0)
        return Box(0.5 * (pmin + pmax), tf3d.quaternions.qeye(), pmax - pmin)

    @classmethod
    def _get_ice_cls(cls):
        slice_loader.load_armarx_slice("RobotAPI", "objectpose/object_pose_types.ice")
        from armarx.objpose import Box

        return Box

    def _set_from_ice(self, dto):
        self.position = self._vec3_conv.from_ice(dto.position)
        self.orientation = self._quat_conv.from_ice(dto.orientation)
        self.extents = self._vec3_conv.from_ice(dto.extents)

    def _set_to_ice(self, dto):
        dto.position = self._vec3_conv.to_ice(self.position)
        dto.orientation = self._quat_conv.to_ice(self.orientation)
        dto.extents = self._vec3_conv.to_ice(self.extents)

    @property
    def _vec3_conv(self) -> Vector3BaseConv:
        if self.__vec3_conv is None:
            self.__vec3_conv = Vector3BaseConv()
        return self.__vec3_conv

    @property
    def _quat_conv(self) -> QuaternionBaseConv:
        if self.__quat_conv is None:
            self.__quat_conv = QuaternionBaseConv()
        return self.__quat_conv

    def __repr__(self):
        return "<{c} pos={p} ori={o} ext={e}>".format(
            c=self.__class__.__name__,
            p=self.position,
            o=self.orientation,
            e=self.extents,
        )
