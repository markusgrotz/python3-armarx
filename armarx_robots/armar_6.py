import time
from typing import Dict
from functools import lru_cache

from armarx_robots.basic_robot import Robot

from armarx import KinematicUnitInterfacePrx

# from armarx import KinematicUnitObserverInterfacePrx

from armarx import ControlMode

from armarx_robots.statechart import StatechartExecutor
from armarx_robots.sensors import Camera


class A6(Robot):
    """
    ARMAR-6

    .. highlight:: python
    .. code-block:: python

        from armarx.robots import A6
        robot = A6()
        robot.say('hello world')
    """

    profile_name = "Armar6Real"

    def __init__(self):
        super().__init__()
        self.both_arms_joint_names = [
            "ArmL1_Cla1",
            "ArmL2_Sho1",
            "ArmL3_Sho2",
            "ArmL4_Sho3",
            "ArmL5_Elb1",
            "ArmL6_Elb2",
            "ArmL7_Wri1",
            "ArmL8_Wri2",
            "ArmR1_Cla1",
            "ArmR2_Sho1",
            "ArmR3_Sho2",
            "ArmR4_Sho3",
            "ArmR5_Elb1",
            "ArmR6_Elb2",
            "ArmR7_Wri1",
            "ArmR8_Wri2",
        ]
        self.on_connect()
        self.rgbd_camera = Camera('OpenNIPointCloudProvider')
        self.stereo_camera = Camera('RCPointCloudProvider')

        # self.poses =

    def on_connect(self):
        super().on_connect()
        # self.kinematic_observer = KinematicUnitObserverInterfacePrx.get_proxy('Armar6KinematicUnitObserver')

    @property
    @lru_cache(1)
    def kinematic_unit(self):
        return KinematicUnitInterfacePrx.get_proxy("Armar6KinematicUnit")

    def init_pose(self):
        """
        Sets the joint to a default pose
        """
        joint_angles = {
            "ArmL1_Cla1": 0.036781,
            "ArmL2_Sho1": 0.839879,
            "ArmL3_Sho2": 0.111953,
            "ArmL4_Sho3": 0.178885,
            "ArmL5_Elb1": 1.317399,
            "ArmL6_Elb2": -0.077956,
            "ArmL7_Wri1": 0.081407,
            "ArmL8_Wri2": 0.171840,
            "ArmR1_Cla1": -0.036818,
            "ArmR2_Sho1": -0.839400,
            "ArmR3_Sho2": 0.111619,
            "ArmR4_Sho3": -0.179005,
            "ArmR5_Elb1": 1.319545,
            "ArmR6_Elb2": 0.078254,
            "ArmR7_Wri1": -0.081144,
            "ArmR8_Wri2": 0.171887,
            "Neck_1_Yaw": 0.0,
            "Neck_2_Pitch": 0.2,
            "TorsoJoint": 0.5,
        }
        self.move_joints(joint_angles)

    def save_pose(self, pose_name: str):
        """
        ..todo:: retrieve current pose and store under name
        """
        pass

    def set_pose(self, pose_name: str):
        """ """
        pass

    def both_arms_zero_torque(self, joint_names=None):
        """
        Sets zero torque mode for both arms
        """
        joint_names = joint_names or self.both_arms_joint_names
        control_mode = {n: ControlMode.eTorqueControl for n in joint_names}
        joint_torques = {n: 0 for n in joint_names}
        self.kinematic_unit.switchControlMode(control_mode)
        self.kinematic_unit.setJointTorques(joint_torques)

    def place_object(self, state_parameters=None):
        s = StatechartExecutor(self.profile_name, "Armar6GraspingGroup", "PlaceObject")
        return s.run(state_parameters, True)

    def grasp_object(self, state_parameters=None):
        s = StatechartExecutor(
            self.profile_name, "Armar6GraspingGroup", "GraspSingleObject"
        )
        return s.run(state_parameters, True)
