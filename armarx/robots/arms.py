from armarx import HandUnitInterfacePrx


class Bimanual:
    @property
    def left_hand(self):
        return HandUnitInterfacePrx.get_proxy("LeftHandUnit")

    @property
    def right_hand(self):
        return HandUnitInterfacePrx.get_proxy("RightHandUnit")

    def open_hand(self, hand_name="left, right", shape_name=None):
        """
        Opens a hand or both hands

        :param hand_name: the name of the hand
        :param shape_name: the name of the hand shape
        """
        shape_name = shape_name or "Open"
        if "left" in hand_name:
            self.left_hand.setShape(shape_name)
        if "right" in hand_name:
            self.right_hand.setShape(shape_name)
        if "both" in hand_name:
            self.left_hand.setShape(shape_name)
            self.right_hand.setShape(shape_name)

    def close_hand(self, hand_name="left, right", shape_name=None):
        """
        Closes a hand or both hands

        :param hand_name: the name of the hand
        :param shape_name: the name of the hand shape
        """
        shape_name = shape_name or "Close"
        if "left" in hand_name:
            self.left_hand.setShape(shape_name)
        if "right" in hand_name:
            self.right_hand.setShape(shape_name)
        if "both" in hand_name:
            self.left_hand.setShape(shape_name)
            self.right_hand.setShape(shape_name)
