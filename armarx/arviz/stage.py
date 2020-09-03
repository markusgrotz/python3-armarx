from typing import List, Union, Tuple

from .layer import Layer
from .elements.elements import Pose


class Stage:

    def __init__(self, component: str):
        self.component = component
        self.layers: List[Layer] = []

    def layer(self, name) -> Layer:
        """
        Create a layer.
        :param name: The layer's name.
        :return: The layer.
        """
        layer = Layer(self.component, name)
        self.layers.append(layer)
        return layer

    def origin_layer(self, layer_name="Origin", id="Origin", scale=1.0) -> Layer:
        layer = self.layer(layer_name)
        layer.add(Pose(id, scale=scale))
        return layer

    def __repr__(self):
        return "<{} with {} layers>".format(
            self.__class__.__name__, len(self.layers))

    def __enter__(self):
        """
        Makes a stage usable in a with statement:
        with arviz.begin_stage() as stage:
            with stage.layer("MyLayer") as layer:
                layer.elements += [ ... ]
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
