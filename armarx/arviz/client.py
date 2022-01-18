import enum
import logging
import numpy as np

from typing import List, Union

from armarx import slice_loader, ice_manager

from armarx.ice_conv.ice_converter import IceConverter
from armarx.math.transform import Transform
from armarx.arviz.layer import Layer
from armarx.arviz.stage import Stage

slice_loader.load_armarx_slice("RobotAPI", "ArViz/Component.ice")
import armarx.viz  # The Ice namespace

logger = logging.getLogger(__name__)


class GlobalPoseConv(IceConverter):

    @classmethod
    def _import_dto(cls):
        return armarx.viz.data.GlobalPose

    def _to_ice(self, bo: Transform, *args, **kwargs):
        dto = self.get_dto()()
        dto.x, dto.y, dto.z = bo.translation
        dto.qw, dto.qx, dto.qy, dto.qz = map(float, bo.rot_quat)
        return dto

    def _from_ice(self, dto: armarx.viz.data.GlobalPose, *args, **kwargs):
        return Transform(translation=(dto.x, dto.y, dto.z),
                         rotation=(dto.qw, dto.qx, dto.qy, dto.qz))


class InteractionFeedbackType(enum.IntFlag):
    None_ = 0

    Select = 1
    Deselect = 2

    ContextMenuChosen = 3

    Transform = 4


class InteractionFeedback:

    def __init__(
            self,
            data: armarx.viz.data.InteractionFeedback,
    ):
        """
                    component: str = "",
                    layer: str = "",
                    element: str = "",
                    revision: int = 0,
                    chosen_context_menu_entry: int = 0,
                    transformation: Transform = None,
                    scale: np.ndarray = None,
                    """
        self._data = data

        from armarx.ice_conv.armarx_core.basic_vector_types import Vector3fConv
        self.vector3f_conv = Vector3fConv()
        self.global_pose_conv = GlobalPoseConv()


    @property
    def type(self) -> InteractionFeedbackType:
        # Mask out all the flags in the higher bits
        ice_type = self._data.type & 0x7
        Types = InteractionFeedbackType
        IceTypes = armarx.viz.data.InteractionFeedbackType

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
        return self._data.type & armarx.arviz.data.InteractionFeedbackType.TRANSFORM_BEGIN_FLAG

    @property
    def is_transform_during(self) -> bool:
        return self._data.type & armarx.arviz.data.InteractionFeedbackType.TRANSFORM_DURING_FLAG

    @property
    def is_transform_end(self) -> bool:
        return self._data.type & armarx.arviz.data.InteractionFeedbackType.TRANSFORM_ENDFLAG

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
        global_pose: armarx.viz.data.GlobalPose = self._data.transformation
        return self.global_pose_conv.from_ice(global_pose)

    @property
    def scale(self) -> np.ndarray:
        """
        :return: The scale as [x, y, z] array.
        """
        scale: armarx.Vector3f = self._data.scale
        return self.vector3f_conv.from_ice(scale)


class CommitResult:

    def __init__(
            self,
            data: armarx.viz.data.CommitResult,
    ):
        self._data = data
        ice_interactions: List[armarx.viz.data.InteractionFeedback] = self._data.interactions
        self.interactions = [InteractionFeedback(data) for data in ice_interactions]

    @property
    def revision(self) -> int:
        return self._data.revision


class Client:
    """
    An ArViz client.
    """

    STORAGE_DEFAULT_NAME = "ArVizStorage"

    def __init__(
            self,
            component: str,
            storage_name=STORAGE_DEFAULT_NAME,
            wait_for_proxy=True,
    ):
        self.component_name = component

        args = (armarx.viz.StorageInterfacePrx, storage_name)
        if wait_for_proxy:
            self.storage = ice_manager.wait_for_proxy(*args)
        else:
            self.storage = ice_manager.get_proxy(*args)

    def layer(self, name) -> Layer:
        """
        Create a layer.
        :param name: The layer's name.
        :return: The layer.
        """
        return Layer(self.component_name, name)

    def begin_stage(self, commit_on_exit=False) -> Stage:
        if commit_on_exit:
            return Stage(self.component_name,
                         commit_on_exit=commit_on_exit, client=self)
        else:
            return Stage(self.component_name)

    def commit(
            self,
            layers_or_stages: Union[None, Layer, Stage, List[Union[Layer, Stage]]] = None,
    ) -> CommitResult:
        """
        Commit the given layers and stages.
        :param layers_or_stages: Layer(s) or Stage(s) to commit.
        """
        if layers_or_stages is None:
            layers_or_stages = []
        try:
            iter(layers_or_stages)
        except TypeError:
            # Single item.
            layers_or_stages = [layers_or_stages]

        input_ = armarx.viz.data.CommitInput()
        input_.updates = sum(map(self._get_layer_updates, layers_or_stages), [])
        input_.interactionComponent = self.component_name

        interaction_layers: List[str] = []

        for layer_or_stage in layers_or_stages:
            if isinstance(layer_or_stage, Stage):
                stage = layer_or_stage
                interaction_layers += stage._interaction_layers

        input_.interactionLayers = interaction_layers


        ice_result = self.storage.commitAndReceiveInteractions(input_)

        result = CommitResult(data=ice_result)
        return result

    @staticmethod
    def _get_layer_updates(
            layer_like: Union[Layer, armarx.viz.data.LayerUpdate]) \
            -> List[armarx.viz.data.LayerUpdate]:

        if isinstance(layer_like, armarx.viz.data.LayerUpdate):
            return [layer_like]
        elif isinstance(layer_like, Layer):
            return [layer_like.data()]
        elif isinstance(layer_like, Stage):
            return [layer.data() for layer in layer_like.layers]
        else:
            logger.warn('Unable to get layer updates')
            return []
