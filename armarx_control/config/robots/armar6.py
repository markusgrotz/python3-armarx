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
