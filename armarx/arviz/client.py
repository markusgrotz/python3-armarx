import logging

from typing import List, Union

from armarx import slice_loader
from armarx.ice_manager import get_topic

slice_loader.load_armarx_slice("RobotAPI", "ArViz/Component.ice")
import armarx.viz  # The Ice namespace

from .layer import Layer
from .stage import Stage


logger = logging.getLogger(__name__)


class Client:
    """
    An ArViz client.
    """

    def __init__(self, component: str, topic_name="ArVizTopic"):
        self.component_name = component
        self.topic = get_topic(armarx.viz.TopicPrx, topic_name)

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

    def commit(self, layers_or_stages: Union[None, Layer, Stage, List[Union[Layer, Stage]]] = None):
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

        self.topic.updateLayers(sum(map(self._get_layer_updates, layers_or_stages), []))

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
