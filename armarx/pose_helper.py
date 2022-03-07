import numpy as np
import transforms3d as tf3d

from armarx import RobotStateComponentInterfacePrx
from armarx import FramedPositionBase
from armarx import FramedPoseBase
from armarx import FramedOrientationBase

def pose2mat(pose: FramedPoseBase) -> np.ndarray:
    """
    Converts a FramedPoseBase to a homogeneous matrix

    :param pose: FramedPoseBase
    :return: numpy.ndarry
    """
    qw = pose.orientation.qw
    qx = pose.orientation.qx
    qy = pose.orientation.qy
    qz = pose.orientation.qz
    rot_mat = tf3d.quaternions.quat2mat([qw, qx, qy, qz])
    transform_mat = np.identity(4)
    transform_mat[0:3, 0:3] = rot_mat
    position = pose.position
    transform_mat[0, 3] = position.x
    transform_mat[1, 3] = position.y
    transform_mat[2, 3] = position.z

    return transform_mat


def convert_position_to_global(f: FramedPositionBase) -> np.ndarray:
    pose = FramedPoseBase(position=f, orientation=FramedOrientationBase(), frame=f.frame, agent=f.agent)
    return convert_pose_to_global(pose)

def convert_mat_to_global(pose: np.ndarray, frame: str) -> np.ndarray:
    robot_state = RobotStateComponentInterfacePrx.get_proxy()
    current_robot_state = robot_state.getSynchronizedRobot()
    robot_pose = current_robot_state.getGlobalPose()
    robot_node = current_robot_state.getRobotNode(frame).getPoseInRootFrame()
    transform_robot_node_to_root = pose2mat(robot_node)
    transform_root_to_global = pose2mat(robot_pose)

    return np.dot(transform_root_to_global, np.dot(transform_robot_node_to_root, pose))


def convert_mat_to_root(pose: np.ndarray, frame: str) -> np.ndarray:
    robot_state = RobotStateComponentInterfacePrx.get_proxy()
    current_robot_state = robot_state.getSynchronizedRobot()
    if frame == 'Global' or frame == 'armarx::Global':
        robot_pose = current_robot_state.getGlobalPose()
        robot_pose[:3, :3] = robot_pose.T
        robot_pose[3, :3] = -1 * np.dot(robot_pose[:3, :3], robot_pose[3, :3])
        return np.dot(robot_pose, pose) 
    else:
        robot_node = current_robot_state.getRobotNode(frame).getPoseInRootFrame()
        transform_robot_node_to_root = pose2mat(robot_node)
        return np.dot(transform_robot_node_to_root, pose)


def convert_pose_to_global(f: FramedPoseBase) -> np.ndarray:
    transform = pose2mat(f)
    return convert_mat_to_global(transform, f.frame)

def convert_pose_to_root(f: FramedPoseBase) -> np.ndarray:
    transform = pose2mat(f)
    return convert_mat_to_root(transform, f.frame)


