import time
from typing import Dict
from functools import lru_cache

from armarx_robots.basic_robot import Robot

from armarx import KinematicUnitInterfacePrx

# from armarx import KinematicUnitObserverInterfacePrx

from armarx import ControlMode

from armarx_robots.statechart import StatechartExecutor


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

        # self.poses =

    def on_connect(self):
        super().on_connect()
        # self.kinematic_observer = KinematicUnitObserverInterfacePrx.get_proxy('Armar6KinematicUnitObserver')

    @Robot.kinematic_unit.setter
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

    def wait_for_joints(self, joint_angles: Dict[str, float], eps=0.1, timeout=5):
        """
        Waits until the robot has reached a pose

        :param eps: angle accuraccy in radiant
        :param timeout: timeout in seconds
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            has_reached = True
            actual_joint_angles = self.kinematic_unit.getJointAngles()
            for joint_name, expected_joint_angle in joint_angles.items():
                actual_joint_angle = actual_joint_angles[joint_name]
                if abs(expected_joint_angle - actual_joint_angle) > eps:
                    has_reached = False
                    break
            if has_reached:
                return True
            else:
                time.sleep(0.05)
        return False

    def both_arms_zero_torque(self, joint_names=None):
        """
        Sets zero torque mode for both arms
        """
        joint_names = joint_names or self.both_arms_joint_names
        control_mode = {n: ControlMode.eTorqueControl for n in joint_names}
        joint_torques = {n: 0 for n in joint_names}
        self.kinematic_unit.switchControlMode(control_mode)
        self.kinematic_unit.setJointTorques(joint_torques)

    def both_arms_zero_velocity(self, joint_names=None):
        """
        Sets zero velocity for both arms
        """
        joint_names = joint_names or self.both_arms_joint_names
        control_mode = {n: ControlMode.eVelocityControl for n in joint_names}
        joint_velocities = {n: 0 for n in joint_names}
        self.kinematic_unit.switchControlMode(control_mode)
        self.kinematic_unit.setJointVelocities(joint_velocities)

    def move_joints(self, joint_angles: Dict[str, float]):
        """
        Sets the joint position

        :param joint_angles: A map containing the joint names and positions.
        """
        control_mode = {
            k: ControlMode.ePositionControl for k, _ in joint_angles.items()
        }
        self.kinematic_unit.switchControlMode(control_mode)
        self.kinematic_unit.setJointAngles(joint_angles)

    def place_object(self, state_parameters=None):
        s = StatechartExecutor(self.profile_name, "Armar6GraspingGroup", "PlaceObject")
        return s.run(state_parameters, True)

    def grasp_object(self, state_parameters=None):
        s = StatechartExecutor(
            self.profile_name, "Armar6GraspingGroup", "GraspSingleObject"
        )
        return s.run(state_parameters, True)
