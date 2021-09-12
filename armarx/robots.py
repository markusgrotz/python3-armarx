import sys
import logging
import threading
import time

from armarx import ice_manager

from armarx import PlatformNavigatorInterfacePrx
from armarx import GazeControlInterfacePrx
from armarx import ElasticFusionInterfacePrx

from armarx.slice_loader import load_armarx_slice
load_armarx_slice('ArmarXCore', 'components/EmergencyStopInterface.ice')
from armarx.ice_manager import get_proxy

from armarx import EmergencyStopMasterInterfacePrx
from armarx import EmergencyStopState
from armarx.speech import TextStateListener

logger = logging.getLogger(__name__)

class Robot(object):
    """
    Convenience class 
    """

    def __init__(self):
        self._text_state_listener = TextStateListener()
        self._text_state_listener.register()


        self.navigator = PlatformNavigatorInterfacePrx.get_proxy()
        self.gaze = GazeControlInterfacePrx.get_proxy()
        #self._fusion = ElasticFusionInterfacePrx.get_proxy()

        self.emergency_stop = get_proxy(EmergencyStopMasterInterfacePrx, 'EmergencyStopMaster')


    def say(self, text):
        self._text_state_listener.say(text)

    def scan_scene(self):
        # self._fusion.reset()
        for yaw in [-0.3, 0.0, 0.3]:
            self.gaze.setYaw(yaw)
            time.sleep(0.3)
        self.gaze.setYaw(0.0)

    def stop(self):
        self.emergency_stop.setEmergencyStopState(EmergencyStopState.eEmergencyStopActive)


from armarx import HandUnitInterfacePrx
from armarx import KinematicUnitInterfacePrx
from armarx import KinematicUnitObserverInterfacePrx
from armarx import ControlMode



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
        self.left_hand = HandUnitInterfacePrx.get_proxy('LeftHandUnit')
        self.right_hand = HandUnitInterfacePrx.get_proxy('RightHandUnit')
        self.kinematic_unit = KinematicUnitInterfacePrx.get_proxy('Armar6KinematicUnit')
        self.kinematic_observer = KinematicUnitObserverInterfacePrx.get_proxy('Armar6KinematicUnitObserver')

    def grasp(self, object_name):
        pass

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

    def move_joints(self, joint_angles):
        """
        Sets the joint position

        :param joint_angles: A map containing the joint name and positions.
        """
        control_mode = {k: ControlMode.ePositionControl for k,v in joint_angles.items()}
        self.kinematic_unit.switchControlMode(control_mode)
        self.kinematic_unit.setJointAngles(joint_angles)




