from typing import Dict

from .armar_6 import A6

from armarx import ice_manager

from armarx import HandUnitInterfacePrx
from armarx import KinematicUnitInterfacePrx
from armarx import KinematicUnitObserverInterfacePrx

class AD(A6):

    def __init__(self):
        super().__init__()
        self.profile_name = 'ArmarDEReal'
        self.left_hand = HandUnitInterfacePrx.get_proxy('LeftHandUnit')
        self.right_hand = HandUnitInterfacePrx.get_proxy('RightHandUnit')
        self.kinematic_unit = ice_manager.get_proxy(KinematicUnitInterfacePrx, 'ArmarDEKinematicUnit')
        self.kinematic_observer = KinematicUnitObserverInterfacePrx.get_proxy('ArmarDEKinematicUnitObserver')
        self.both_arms_joint_names = ["ArmL1_Cla1", "ArmL2_Sho1", "ArmL3_Sho2",
                    "ArmL4_Sho3", "ArmL5_Elb1", "ArmL6_Elb2", "ArmL7_Wri1",
                    "ArmL8_Wri2", "ArmR1_Cla1", "ArmR2_Sho1", "ArmR3_Sho2",
                    "ArmR4_Sho3", "ArmR5_Elb1", "ArmR6_Elb2", "ArmR7_Wri1",
                    "ArmR8_Wri2"]
