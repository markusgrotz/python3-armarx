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



