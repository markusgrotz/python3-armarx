from typing import Dict
from functools import lru_cache

from armarx_robots.armar_6 import A6
from armarx_robots.basic_robot import Robot

from armarx_core import ice_manager

from armarx import HandUnitInterfacePrx
from armarx import KinematicUnitInterfacePrx


class AD(A6):
    def __init__(self):
        super().__init__()
        self.profile_name = "ArmarDEReal"
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

    def on_connect(self):
        pass
       # self.kinematic_observer = KinematicUnitObserverInterfacePrx.get_proxy('ArmarDEKinematicUnitObserver')

    @property
    @lru_cache(1)
    def kinematic_unit(self):
        return ice_manager.get_proxy(KinematicUnitInterfacePrx, "KinematicUnit")

