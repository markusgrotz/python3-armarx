import pytest

import numpy as np
import transforms3d as tf3d

from armarx import slice_loader
from armarx.ice_conv.robot_api import pose_base as conv

slice_loader.load_armarx_slice("RobotAPI", "core/PoseBase.ice")
from armarx import Vector3Base, QuaternionBase, PoseBase

vec3_conv = conv.Vector3BaseConv()
quat_conv = conv.QuaternionBaseConv()
pose_conv = conv.PoseBaseConv()


def test_pose_from_ice():
    quat = tf3d.quaternions.axangle2quat((1, 0, 0), np.pi)

    dto_pos = Vector3Base(100, 200, 300)
    dto_quat = QuaternionBase(qw=quat[0], qx=quat[1], qy=quat[2], qz=quat[3])
    dto_pose = PoseBase(position=dto_pos, orientation=dto_quat)

    bo_pose: np.ndarray = pose_conv.from_ice(dto_pose)
    assert isinstance(bo_pose, np.ndarray)
    assert bo_pose.shape == (4, 4)
    assert bo_pose.dtype == np.float64
    assert bo_pose[0, 3] == 100
    assert bo_pose[1, 3] == 200
    assert bo_pose[2, 3] == 300
    assert np.allclose(bo_pose[:3, :3], tf3d.quaternions.quat2mat(quat))


def test_pose_to_ice():
    pos = np.array((100, 200, 300))
    ori = tf3d.axangles.axangle2mat((1, 0, 0), np.pi)
    pose = tf3d.affines.compose(T=pos, R=ori, Z=np.ones(3))

    dto_pose: np.ndarray = pose_conv.to_ice(pose)
    assert isinstance(dto_pose, PoseBase)
    dto_pos = dto_pose.position
    dto_ori = dto_pose.orientation
    assert isinstance(dto_pose.position, Vector3Base)
    assert isinstance(dto_pose.orientation, QuaternionBase)
    assert dto_pos.x == 100
    assert dto_pos.y == 200
    assert dto_pos.z == 300
    assert np.isclose(dto_ori.qw, 0.0)
    assert np.isclose(dto_ori.qx, 1.0)
    assert np.isclose(dto_ori.qy, 0.0)
    assert np.isclose(dto_ori.qz, 0.0)
