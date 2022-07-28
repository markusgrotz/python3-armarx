from typing import Dict

from .basic_robot import Robot

from armarx import ice_manager

from armarx import KinematicUnitInterfacePrx
from armarx import ViewSelectionInterfacePrx
from armarx import ViewTargetBase

from armarx.statechart import StatechartExecutor

class A3(Robot):
    """
    ARMAR-III

    .. highlight:: python
    .. code-block:: python

        from armarx.robots import A3
        robot = A3()
        robot.say('hello world')
    """

    profile_name = 'Armar3Real'

    def __init__(self):
        super().__init__()
        self.on_connect()

    def on_connect(self):
        super().on_connect()
        self.kinematic_unit = KinematicUnitInterfacePrx.get_proxy('Armar3KinematicUnit')

        class GazeSelection:

            def __init__(self):
                self.view_selection = ViewSelectionInterfacePrx.get_proxy()

            def fixate(self, target, timeout=0):
                self.view_selection.addManualViewTarget(target)

        self.gaze = GazeSelection()

    def move_to(self, state_parameters=None):
        s = StatechartExecutor(self.profile_name, 'PlatformGroup', 'MovePlatform')
        return s.run(state_parameters, True)

    def bring_object(self, state_parameters=None):
        s = StatechartExecutor(self.profile_name, 'BringObject', '')
        return s.run(state_parameters, True)

    def grasp_object(self, state_parameters=None):
        s = StatechartExecutor(self.profile_name, 'GraspObjectGroup', 'GraspSingleObject')
        return s.run(state_parameters, True)
