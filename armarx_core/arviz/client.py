import logging

from typing import List, Union

from armarx import ice_manager

from armarx.arviz.layer import Layer
from armarx.arviz.stage import Stage
from armarx.arviz.interaction_feedback import CommitResult
from armarx.viz import StorageInterfacePrx
import armarx.viz as viz

logger = logging.getLogger(__name__)


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

        args = (viz.StorageInterfacePrx, storage_name)
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
            return Stage(
                self.component_name, commit_on_exit=commit_on_exit, client=self
            )
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

        input_ = viz.data.CommitInput()
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
        layer_like: Union[Layer, viz.data.LayerUpdate],
    ) -> List[viz.data.LayerUpdate]:

        if isinstance(layer_like, viz.data.LayerUpdate):
            return [layer_like]
        elif isinstance(layer_like, Layer):
            return [layer_like.data()]
        elif isinstance(layer_like, Stage):
            return [layer.data() for layer in layer_like.layers]
        else:
            logger.warning("Unable to get layer updates.")
            return []
