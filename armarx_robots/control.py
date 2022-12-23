import time
import logging

from typing import List
from typing import Dict
from typing import Any

import numpy as np

from armarx.pose_helper import convert_pose_to_global
from armarx.pose_helper import convert_pose_to_root
from armarx import RobotUnitInterfacePrx
from armarx import NJointCartesianWaypointControllerConfig
from armarx import NJointCartesianWaypointControllerInterfacePrx
from armarx import Matrix_4_4_f as Matrix4f
from armarx import Vector4f

from armarx import FramedPoseBase

from armarx import Vector3Base
from armarx import QuaternionBase


logger = logging.getLogger(__name__)



from abc import ABC
from abc import abstractmethod

class AbstractController(ABC):

        
    @property
    @abstractmethod
    def controller_name(self) -> str:
        pass

            
    @property
    @abstractmethod
    def config(self) -> Dict[str, Any]:
        pass

class CartesianWaypointController:

    controller_name: str = 'NJointCartesianWaypointController'
    config = {'rns' : 'RightArm'}

    def __init__(self, config = None, name: str = None):
        if not config:
            self.config.update(config)
        self.controller = None
        self.name = name or self.__class__.__name__
        self.robot_unit = RobotUnitInterfacePrx.get_proxy('Armar6Unit')


    def __enter__(self):
        config = NJointCartesianWaypointControllerConfig(**self.config)
        controller = self.robot_unit.createOrReplaceNJointController(self.controller_name, self.name, config)

        controller = NJointCartesianWaypointControllerInterfacePrx.checkedCast(controller)
        self.controller = controller
        controller.activateController()

        return controller


    def __del__(self):
        if self.controller:
            self.controller.deleteController()


    def __exit__(self, exc_type, exc_value, traceback):
        if  not self.controller:
            return

        self.controller.deactivateController()
        while self.controller.isControllerActive():
            logger.debug('Waiting until controller is deactived')
            time.sleep(0.01)

