import enum
import numpy as np

from typing import List
from armarx.math.transform import Transform


from armarx import Vector3f
from armarx.viz.data import Element
from armarx.viz.data import InteractionFeedback
from armarx.viz.data import InteractionFeedbackType
from armarx.viz.data import CommitResult


class InteractionFeedbackType(enum.IntFlag):
    None_ = 0

    Select = 1
    Deselect = 2

    ContextMenuChosen = 3

    Transform = 4


class InteractionFeedback:
    def __init__(
        self,
        data: InteractionFeedback,
    ):
        self._data = data

    @property
    def type(self) -> InteractionFeedbackType:
        # Mask out all the flags in the higher bits
        ice_type = self._data.type & 0x7
        Types = InteractionFeedbackType
        IceTypes = InteractionFeedbackType

        type_dict = {
            IceTypes.NONE: Types.None_,
            IceTypes.SELECT: Types.Select,
            IceTypes.DESELECT: Types.Deselect,
            IceTypes.CONTEXT_MENU_CHOSEN: Types.ContextMenuChosen,
            IceTypes.TRANSFORM: Types.Transform,
        }

        try:
            return type_dict[ice_type]
        except KeyError:
            raise ValueError(f"Unexpected InteractionFeedbackType {ice_type}.")

    @property
    def is_transform_begin(self) -> bool:
        return self._data.type & InteractionFeedbackType.TRANSFORM_BEGIN_FLAG

    @property
    def is_transform_during(self) -> bool:
        return self._data.type & InteractionFeedbackType.TRANSFORM_DURING_FLAG

    @property
    def is_transform_end(self) -> bool:
        return self._data.type & InteractionFeedbackType.TRANSFORM_END_FLAG

    @property
    def layer(self) -> str:
        return self._data.layer

    @property
    def element(self) -> str:
        return self._data.element

    @property
    def revision(self) -> int:
        return self._data.revision

    @property
    def chosen_context_menu_entry(self) -> int:
        return self._data.chosenContextMenuEntry

    @property
    def transformation(self) -> Transform:

        from armarx.arviz.conv import GlobalPoseConv

        global_pose = self._data.transformation
        return self.global_pose_conv.from_ice(global_pose)

    @property
    def scale(self) -> np.ndarray:
        """
        :return: The scale as [x, y, z] array.
        """
        scale: Vector3f = self._data.scale
        return Vector3f(*scale)


class CommitResult:
    def __init__(
        self,
        data: CommitResult,
    ):
        self._data = data
        ice_interactions: List[InteractionFeedback] = self._data.interactions
        self.interactions = [InteractionFeedback(data) for data in ice_interactions]

    @property
    def revision(self) -> int:
        return self._data.revision
