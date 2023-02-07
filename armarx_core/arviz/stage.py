from typing import List, Union

from .layer import Layer


class Stage:
    def __init__(self, component: str, commit_on_exit=False, client=None):
        self.component = component
        self.commit_on_exit = commit_on_exit
        self.client = client

        self.layers: List[Layer] = []

        self._interaction_component: str = ""
        self._interaction_layers: List[str] = []

    def layer(self, name: str) -> Layer:
        """
        Create a layer.
        :param name: The layer's name.
        :return: The layer.
        """
        layer = Layer(self.component, name)
        self.layers.append(layer)
        return layer

    def add(self, layer_or_layers: Union[Layer, List[Layer]]):
        if isinstance(layer_or_layers, Layer):
            layer = layer_or_layers
            self.layers.append(layer)
        else:
            layers = list(layer_or_layers)
            self.layers += layers

    def reset(self):
        self.layers.clear()
        self._interaction_component = ""
        self._interaction_layers.clear()

    def origin_layer(self, layer_name="Origin", id="Origin", scale=1.0) -> Layer:
        from .elements.elements import Pose

        layer = self.layer(layer_name)
        layer.add(Pose(id, scale=scale))
        return layer

    def request_interaction(self, layer: Layer):
        self._interaction_component = layer.component
        self._interaction_layers.append(layer.name)

    def __repr__(self):
        return "<{} with {} layers>".format(self.__class__.__name__, len(self.layers))

    def __enter__(self):
        """
        Makes a stage usable in a with statement:
        with arviz.begin_stage() as stage:
            with stage.layer("MyLayer") as layer:
                layer.elements += [ ... ]
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.commit_on_exit and self.client is not None:
            self.client.commit(self)
