import logging
import time
import json
import os

from abc import ABC
from abc import abstractmethod

from functools import lru_cache

from armarx import EmergencyStopMasterInterfacePrx
from armarx import EmergencyStopState
from armarx import KinematicUnitInterfacePrx
from armarx import HandUnitInterfacePrx

from armarx_robots.speech import TextStateListener
from armarx_robots.statechart import StatechartExecutor
from armarx_robots.arms import Bimanual


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
    def gaze(self):
        from armarx import GazeControlInterfacePrx

        return GazeControlInterfacePrx.get_proxy()

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
