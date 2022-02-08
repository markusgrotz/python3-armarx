import sys
import logging
import threading
import time
from typing import Dict

from abc import ABC

from armarx import ice_manager

from armarx import KinematicUnitInterfacePrx
from armarx import KinematicUnitObserverInterfacePrx
from armarx import ControlMode
from armarx import HandUnitInterfacePrx

from armarx import PlatformNavigatorInterfacePrx
from armarx import GazeControlInterfacePrx
from armarx import ElasticFusionInterfacePrx

from armarx import EmergencyStopMasterInterfacePrx
from armarx import EmergencyStopState
from armarx.speech import TextStateListener

from armarx.statechart import StatechartExecutor

logger = logging.getLogger(__name__)


class Robot(ABC):
    """
    Convenience class 
    """

    def __init__(self):
        self._text_state_listener = TextStateListener()
        self._text_state_listener.on_connect()

        # self._init_default_names()

        self.navigator = PlatformNavigatorInterfacePrx.get_proxy()
        self.gaze = GazeControlInterfacePrx.get_proxy()
        #self._fusion = ElasticFusionInterfacePrx.get_proxy()

        self.emergency_stop = EmergencyStopMasterInterfacePrx.get_proxy()

        self.profile_name = None

    def what_can_you_see_now(self, state_parameters=None):
        s = StatechartExecutor(self.profile_name, 'ScanLocationGroup', 'WhatCanYouSeeNow')
        return s.run(state_parameters, True)

    def handover(self, state_parameters=None):
        s = StatechartExecutor(self.profile_name, 'HandOverGroup', 'ReceiveFromRobot')
        return s.run(state_parameters, True)

    def say(self, text):
        self._text_state_listener.say(text) 

    def scan_scene(self):
        # self._fusion.reset()
        for yaw in [-0.3, 0.3]:
            self.gaze.setYaw(yaw)
            time.sleep(0.3)
        self.gaze.setYaw(0.0)

    def stop(self):
        self.emergency_stop.setEmergencyStopState(EmergencyStopState.eEmergencyStopActive)

    def _init_default_names(self):
        ax_loader = sys.meta_path[0]
        sys.meta_path.insert(0, ArmarXVariantInfoFinder())



#class AD(A6):
#
#    def __init__(self):
#            super().__init__()
#            self.profile_name = 'ArmarDEReal'
#            self.left_hand = HandUnitInterfacePrx.get_proxy('LeftHandUnit')
#            self.right_hand = HandUnitInterfacePrx.get_proxy('RightHandUnit')
#            self.kinematic_unit = ice_manager.get_proxy(KinematicUnitInterfacePrx, 'ArmarDEKinematicUnit')
#            self.kinematic_observer = KinematicUnitObserverInterfacePrx.get_proxy('ArmarDEKinematicUnitObserver')
#            self.both_arms_joint_names = ["ArmL1_Cla1", "ArmL2_Sho1", "ArmL3_Sho2",
#                        "ArmL4_Sho3", "ArmL5_Elb1", "ArmL6_Elb2", "ArmL7_Wri1",
#                        "ArmL8_Wri2", "ArmR1_Cla1", "ArmR2_Sho1", "ArmR3_Sho2",
#                        "ArmR4_Sho3", "ArmR5_Elb1", "ArmR6_Elb2", "ArmR7_Wri1",
#                        "ArmR8_Wri2"]
#
#     
        
    
class A6(Robot):
    """
    ARMAR-6

    .. highlight:: python
    .. code-block:: python

        from armarx.robots import A6
        robot = A6()
        robot.say('hello world')
    """

    def __init__(self):
        super().__init__()
        self.profile_name = 'Armar6Real'
        self.left_hand = HandUnitInterfacePrx.get_proxy('LeftHandUnit')
        self.right_hand = HandUnitInterfacePrx.get_proxy('RightHandUnit')
        self.kinematic_unit = ice_manager.get_proxy(KinematicUnitInterfacePrx, 'Armar6KinematicUnit')
        self.kinematic_observer = KinematicUnitObserverInterfacePrx.get_proxy('Armar6KinematicUnitObserver')
        self.both_arms_joint_names = ["ArmL1_Cla1", "ArmL2_Sho1", "ArmL3_Sho2",
                "ArmL4_Sho3", "ArmL5_Elb1", "ArmL6_Elb2", "ArmL7_Wri1",
                "ArmL8_Wri2", "ArmR1_Cla1", "ArmR2_Sho1", "ArmR3_Sho2",
                "ArmR4_Sho3", "ArmR5_Elb1", "ArmR6_Elb2", "ArmR7_Wri1",
                "ArmR8_Wri2"]

        #self.poses = 


    def open_hand(self, hand_name='left, right', shape_name=None):
        """
        Opens a hand or both hands

        :param hand_name: the name of the hand
        :param shape_name: the name of the hand shape
        """
        shape_name = shape_name or 'Open'
        if 'left' in hand_name:
            self.left_hand.setShape(shape_name)
        if 'right' in hand_name:
            self.right_hand.setShape(shape_name)
        if 'both' in hand_name:
            self.left_hand.setShape(shape_name)
            self.right_hand.setShape(shape_name)

    def close_hand(self, hand_name='left, right', shape_name=None):
        """
        Closes a hand or both hands

        :param hand_name: the name of the hand
        :param shape_name: the name of the hand shape
        """
        shape_name = shape_name or 'Close'
        if 'left' in hand_name:
            self.left_hand.setShape(shape_name)
        if 'right' in hand_name:
            self.right_hand.setShape(shape_name)
        if 'both' in hand_name:
            self.left_hand.setShape(shape_name)
            self.right_hand.setShape(shape_name)


    def init_pose(self):
        """
        Sets the joint to a default pose
        """
        joint_angles = {"ArmL1_Cla1": 0.036781, "ArmL2_Sho1": 0.839879,
                "ArmL3_Sho2": 0.111953, "ArmL4_Sho3": 0.178885, "ArmL5_Elb1":
                1.317399, "ArmL6_Elb2": -0.077956, "ArmL7_Wri1": 0.081407,
                "ArmL8_Wri2": 0.171840, "ArmR1_Cla1": -0.036818, "ArmR2_Sho1":
                -0.839400, "ArmR3_Sho2": 0.111619, "ArmR4_Sho3": -0.179005,
                "ArmR5_Elb1": 1.319545, "ArmR6_Elb2": 0.078254, "ArmR7_Wri1":
                -0.081144, "ArmR8_Wri2": 0.171887, "Neck_1_Yaw": 0.0,
                "Neck_2_Pitch": 0.2, "TorsoJoint": 0.5}
        self.move_joints(joint_angles)


    def save_pose(self, pose_name: str):
        """
        ..todo:: retrieve current pose and store under name
        """
        pass

    def set_pose(self, pose_name: str):
        """
        """
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
        control_mode = {k: ControlMode.ePositionControl for k, _ in joint_angles.items()}
        self.kinematic_unit.switchControlMode(control_mode)
        self.kinematic_unit.setJointAngles(joint_angles)


    def place_object(self, state_parameters=None):
        s = StatechartExecutor(self.profile_name, 'Armar6GraspingGroup', 'PlaceObject')
        return s.run(state_parameters, True)

    def grasp_object(self, state_parameters=None):
        s = StatechartExecutor(self.profile_name, 'Armar6GraspingGroup', 'GraspSingleObject')
        return s.run(state_parameters, True)

