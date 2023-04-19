import logging
import time
import json
import os

from abc import ABC
from abc import abstractmethod

from functools import lru_cache

import armarx_core

from armarx import EmergencyStopMasterInterfacePrx
from armarx import EmergencyStopState
from armarx import KinematicUnitInterfacePrx
from armarx import HandUnitInterfacePrx

from armarx_robots.speech import TextStateListener
from armarx_robots.statechart import StatechartExecutor
from armarx_robots.arms import Bimanual
from typing import Dict

from armarx import ControlMode

logger = logging.getLogger(__name__)


class Robot(ABC, Bimanual):
    """
    Convenience class
    """

    def __init__(self):
        self._text_state_listener = TextStateListener()

    def on_connect(self):
        self._text_state_listener.on_connect()

        # from armarx import ElasticFusionInterfacePrx
        # self._fusion = ElasticFusionInterfacePrx.get_proxy()

    @property
    @abstractmethod
    def kinematic_unit(self):
        pass

    @property
    @lru_cache(1)
    def emergency_stop(self):
        return EmergencyStopMasterInterfacePrx.get_proxy()

    @property
    @lru_cache(1)
    def navigator(self):
        from armarx import PlatformNavigatorInterfacePrx

        return PlatformNavigatorInterfacePrx.get_proxy()

    @property
    @abstractmethod
    def profile_name(self) -> str:
        pass

    def __str__(self) -> str:
        return f"Robot - {self.profile_name}"

    def load_robot_config(self):
        config_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(config_path, "robot_config.json")
        with open(config_path) as f:
            robot_config = json.load(f)
        return robot_config

    def what_can_you_see_now(self, state_parameters=None):
        statechart = StatechartExecutor(
            self.profile_name, "ScanLocationGroup", "WhatCanYouSeeNow"
        )
        return statechart.run(state_parameters, True)

    def handover(self, state_parameters=None):
        statechart = StatechartExecutor(
            self.profile_name, "HandOverGroup", "ReceiveFromRobot"
        )
        return statechart.run(state_parameters, True)

    def navigate_to_location(self, location_name: str, state_parameters=None):

        state_parameters = state_parameters or {}
        state_parameters["location"] = location_name

        statechart = StatechartExecutor(
            self.profile_name, "NavigationGroup", "NavigateToLocation"
        )
        return statechart.run(state_parameters, True)

    def navigate_to(self, x, y, yaw, state_parameters=None):
        from armarx import Vector3Base

        state_parameters = state_parameters or {}
        state_parameters["TargetPosition"] = Vector3Base(x, y, yaw)

        statechart = StatechartExecutor(
            self.profile_name, "NavigationGroup", "NavigateToLocation"
        )
        return statechart.run(state_parameters, True)

    def say(self, text):
        """
        Verbalizes the given text.  SSML markup is supported
        For exmaple, to verbalize in a different language use

        .. highlight:: python
        .. code-block:: python

            robot = Robot()
            robot.say('<speak><voice language="de-de">Hallo Welt</voice></speak>')

        ..see:: armarx.speech.TextStateListener.say()
        """
        self._text_state_listener.say(text)

    def scan_scene(self):
        # self._fusion.reset()
        for yaw in [-0.3, 0.3]:
            self.gaze.setYaw(yaw)
            time.sleep(0.3)
        self.gaze.setYaw(0.0)

    def stop(self):
        """
        Sets the soft emergency stop flag

        If supported by the robot then now motor commands are sent to the
        hardware
        """
        self.emergency_stop.setEmergencyStopState(
            EmergencyStopState.eEmergencyStopActive
        )

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
