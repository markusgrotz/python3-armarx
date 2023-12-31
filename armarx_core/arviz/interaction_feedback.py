import enum
import numpy as np

from typing import List
from armarx_core.math.transform import Transform
from armarx_core.arviz.conv import GlobalPoseConv
from armarx_core.ice_conversion.armarx_core.basic_vector_types import Vector3fConv

from armarx import Vector3f
from armarx.viz.data import InteractionFeedback as InteractionFeedbackIce
from armarx.viz.data import InteractionFeedbackType as InteractionFeedbackTypeIce
from armarx.viz.data import CommitResult as CommitResultIce


class InteractionFeedbackType(enum.IntFlag):
    None_ = 0

    Select = 1
    Deselect = 2

    ContextMenuChosen = 3

    Transform = 4


class InteractionFeedback:
    def __init__(
        self,
        data: InteractionFeedbackIce,
    ):
        self._data = data
        self.global_pose_conv = GlobalPoseConv()
        self.vector3_conv = Vector3fConv()

    @property
    def type(self) -> InteractionFeedbackType:
        # Mask out all the flags in the higher bits
        ice_type = self._data.type & 0x7
        Types = InteractionFeedbackType
        IceTypes = InteractionFeedbackTypeIce

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
        return self._data.type & InteractionFeedbackTypeIce.TRANSFORM_BEGIN_FLAG

    @property
    def is_transform_during(self) -> bool:
        return self._data.type & InteractionFeedbackTypeIce.TRANSFORM_DURING_FLAG

    @property
    def is_transform_end(self) -> bool:
        return self._data.type & InteractionFeedbackTypeIce.TRANSFORM_END_FLAG

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
        global_pose = self._data.transformation
        return self.global_pose_conv.from_ice(global_pose)

    @property
    def scale(self) -> np.ndarray:
        """
        :return: The scale as [x, y, z] array.
        """
        scale: Vector3f = self._data.scale
        return self.vector3_conv.from_ice(scale)


class CommitResult:
    def __init__(
        self,
        data: CommitResultIce,
    ):
        self._data = data
        ice_interactions: List[InteractionFeedback] = self._data.interactions
        self.interactions = [InteractionFeedback(data) for data in ice_interactions]

    @property
    def revision(self) -> int:
        return self._data.revision
