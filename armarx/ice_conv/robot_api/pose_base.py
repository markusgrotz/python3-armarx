import numpy as np
import transforms3d as tf3d

from armarx import slice_loader
from armarx_memory.ice_conv.ice_converter import IceConverter

SLICE_INCLUDE = ("RobotAPI", "core/PoseBase.ice")


class Vector3BaseConv(IceConverter):
    @classmethod
    def _import_dto(cls):
        slice_loader.load_armarx_slice(*SLICE_INCLUDE)
        import armarx

        return armarx.Vector3Base

    def _from_ice(self, dto: "armarx.Vector3Base") -> np.ndarray:
        return np.array([dto.x, dto.y, dto.z])

    def _to_ice(self, bo: np.ndarray) -> "armarx.Vector3Base":
        Vector3Base = self.get_dto()
        x, y, z = bo
        return Vector3Base(x, y, z)


class QuaternionBaseConv(IceConverter):
    @classmethod
    def _import_dto(cls):
        slice_loader.load_armarx_slice(*SLICE_INCLUDE)
        import armarx

        return armarx.QuaternionBase

    def _from_ice(self, dto: "armarx.QuaternionBase") -> np.ndarray:
        return np.array([dto.qw, dto.qx, dto.qy, dto.qz])

    def _to_ice(self, bo: np.ndarray) -> "armarx.QuaternionBase":
        import transforms3d as tf3d

        QuaternionBase = self.get_dto()

        ori = np.array(bo)
        if ori.shape == (3, 3):
            q = tf3d.quaternions.mat2quat(ori)
        else:
            q = ori
        w, x, y, z = q
        return QuaternionBase(w, x, y, z)


class PoseBaseConv(IceConverter):
    def __init__(self):
        super().__init__()
        self.vector3_conv = Vector3BaseConv()
        self.quaternion_conv = QuaternionBaseConv()

    @classmethod
    def _import_dto(cls):
        slice_loader.load_armarx_slice(*SLICE_INCLUDE)
        import armarx

        return armarx.PoseBase

    def _from_ice(self, dto: "armarx.PoseBase") -> np.ndarray:
        import transforms3d as tf3d

        pos = self.vector3_conv.from_ice(dto.position)
        ori = self.quaternion_conv.from_ice(dto.orientation)
        ori = tf3d.quaternions.quat2mat(ori)
        mat: np.ndarray = tf3d.affines.compose(T=pos, R=ori, Z=np.ones(3))
        assert mat.shape == (4, 4)
        assert np.all(mat[3, :3] == 0)
        assert mat[3, 3] == 1
        return mat

    def _to_ice(self, bo: np.ndarray) -> "armarx.PoseBase":
        PoseBase = self.get_dto()
        T, R, _, _ = tf3d.affines.decompose(bo)
        pos = self.vector3_conv.to_ice(T)
        ori = self.quaternion_conv.to_ice(R)
        return PoseBase(position=pos, orientation=ori)
