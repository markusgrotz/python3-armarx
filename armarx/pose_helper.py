"""
Convenience module to convert armarx.FramedPose and armarx.FramedPosition to
numpy arrays and vice versa.

Please note that the numpy array's data type must be np.float32
"""

import numpy as np
import transforms3d as tf3d

from armarx import slice_loader

slice_loader.load_armarx_slice("ArmarXCore", "components/EmergencyStopInterface.ice")
slice_loader.load_armarx_slice(
    "ArmarXCore", "components/SimpleStatechartExecutorInterface.ice"
)

from armarx import RobotStateComponentInterfacePrx
from armarx import FramedPositionBase
from armarx import FramedPoseBase
from armarx import FramedOrientationBase

from armarx import PoseBase
from armarx import Vector3Base
from armarx import QuaternionBase


def mat2pose(pose: np.ndarray, frame: str = None, agent: str = None) -> FramedPoseBase:
    q = tf3d.quaternions.mat2quat(pose[:3, :3])
    q = QuaternionBase(*q)
    v = Vector3Base(*pose[:3, 3])
    if not frame:
        return PoseBase(v, q)
    else:
        return FramedPoseBase(v, q, frame=frame, agent=agent)


def pose2mat(pose: FramedPoseBase) -> np.ndarray:
    """
    Converts a FramedPoseBase to a homogeneous matrix

    Does not change the coordinate system

    :param pose: FramedPoseBase
    :return: numpy.ndarry
    """
    qw = pose.orientation.qw
    qx = pose.orientation.qx
    qy = pose.orientation.qy
    qz = pose.orientation.qz
    rot_mat = tf3d.quaternions.quat2mat([qw, qx, qy, qz])
    transform_mat = np.identity(4, dtype=np.float32)
    transform_mat[0:3, 0:3] = rot_mat
    position = pose.position
    transform_mat[0, 3] = position.x
    transform_mat[1, 3] = position.y
    transform_mat[2, 3] = position.z
    return transform_mat


def convert_position_to_global(f: FramedPositionBase) -> np.ndarray:
    pose = FramedPoseBase(
        position=f, orientation=FramedOrientationBase(), frame=f.frame, agent=f.agent
    )
    return convert_pose_to_global(pose)


def convert_mat_to_global(pose: np.ndarray, frame: str) -> np.ndarray:
    robot_state = RobotStateComponentInterfacePrx.get_proxy()
    current_robot_state = robot_state.getSynchronizedRobot()
    robot_pose = current_robot_state.getGlobalPose()
    robot_node = current_robot_state.getRobotNode(frame).getPoseInRootFrame()
    transform_robot_node_to_root = pose2mat(robot_node)
    transform_root_to_global = pose2mat(robot_pose)


def inv(pose: np.ndarray) -> np.ndarray:
    """
    can be also done by np.linalg.inv but this is a little bit faster
    """
    inv_pose = pose.copy()
    inv_pose[:3, :3] = pose[:3, :3].T
    inv_pose[:3, 3] = -1 * np.dot(pose[:3, :3].T, pose[:3, 3])
    return inv_pose


def robot_state(timestamp: int = None):
    """
    Convenience method to get the robot state. If not timestamp is given return
    the current state
    """
    robot_state = RobotStateComponentInterfacePrx.get_proxy()
    if timestamp:
        return robot_state.getRobotSnapshotAtTimestamp(timestamp)
    return robot_state.getSynchronizedRobot()


def convert_mat_to_robot_node(
    pose: np.ndarray, frame: str, timestamp: int = None
) -> np.ndarray:
    """
    given a global pose

    inverse of convert_mat_to_global
    """
    current_robot_state = robot_state(timestamp)

    robot_node_pose = pose2mat(current_robot_state.getRobotNode(frame).getGlobalPose())
    return np.dot(inv(robot_node_pose), pose)


def convert_mat_to_global(
    pose: np.ndarray, frame: str, timestamp: int = None
) -> np.ndarray:
    current_robot_state = robot_state(timestamp)
    robot_node = current_robot_state.getRobotNode(frame)
    robot_node_pose = pose2mat(robot_node.getGlobalPose())
    return np.dot(robot_node_pose, pose)


def convert_mat_to_root(
    pose: np.ndarray, frame: str, timestamp: int = None
) -> np.ndarray:
    current_robot_state = robot_state(timestamp)
    if frame == "Global" or frame == "armarx::Global":
        robot_pose = pose2mat(current_robot_state.getGlobalPose())
        return np.dot(robot_pose, pose)
    else:
        robot_node = current_robot_state.getRobotNode(frame).getPoseInRootFrame()
        transform_robot_node_to_root = pose2mat(robot_node)
        return np.dot(transform_robot_node_to_root, pose)


def convert_pose_to_global(f: FramedPoseBase) -> np.ndarray:
    """
    Converts a armarx.FramedPoseBase to a numpy array in the global coordinate
    system

    """
    transform = pose2mat(f)
    if f.frame == "Global" or f.frame == "armarx::Global":
        return transform
    return convert_mat_to_global(transform, f.frame)


def convert_pose_to_root(f: FramedPoseBase) -> np.ndarray:
    """
    Converts a armarx.FramedPoseBase to a numpy array
    """
    transform = pose2mat(f)
    return convert_mat_to_root(transform, f.frame)
