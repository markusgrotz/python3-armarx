from armarx_control.config.common import NodeSet, TCP


class Armar6NodeSet(NodeSet):
    LeftArm = "LeftArm"
    RightArm = "RightArm"
    DualArmDefault = "LeftArm,RightArm"

    def get_side(self, node_set):
        d = dict(left=[self.LeftArm], right=[self.RightArm], both=[self.DualArmDefault])
        if node_set in d["left"]:
            return "left"
        elif node_set in d["right"]:
            return "right"
        elif node_set == d["both"]:
            return "both"


class Armar6TCP(TCP):
    LeftArm = "Hand L TCP"
    RightArm = "Hand R TCP"


node_set_map = dict(
    LeftArm=[
        "ArmL1_Cla1",
        "ArmL2_Sho1",
        "ArmL3_Sho2",
        "ArmL4_Sho3",
        "ArmL5_Elb1",
        "ArmL6_Elb2",
        "ArmL7_Wri1",
        "ArmL8_Wri2"
    ],
    RightArm=[
        "ArmR1_Cla1",
        "ArmR2_Sho1",
        "ArmR3_Sho2",
        "ArmR4_Sho3",
        "ArmR5_Elb1",
        "ArmR6_Elb2",
        "ArmR7_Wri1",
        "ArmR8_Wri2"
    ]
)
