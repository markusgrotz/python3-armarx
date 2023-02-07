from typing import List, Union, Tuple


from armarx.viz.data import Element
from armarx.viz.data import LayerUpdate

from .elements import Element as E


class Layer:
    def __init__(self, component: str, name: str, elements: List[E] = ()):
        self.component = component
        self.name = name
        self.elements: List[E] = list(elements)

    def clear(self):
        self.elements = []

    def add(self, element: Union[Element, E]):
        self.elements.append(element)

    @property
    def id(self) -> str:
        return "{}/{}".format(self.component, self.name)

    def data(self) -> LayerUpdate:
        return LayerUpdate(
            component=self.component,
            name=self.name,
            elements=list(map(self._get_element_data, self.elements)),
        )

    @staticmethod
    def _get_element_data(element: Union[Element, E]):
        if isinstance(element, E):
            return element.get_ice_data()
        elif isinstance(element, Element):
            return element
        else:
            raise TypeError(
                "Expected viz element, but received object of class '{}'.".format(
                    element.__class__
                )
            )

    def __iadd__(self, elements):
        """Add an element or multiple elements to this layer's elements."""
        if isinstance(elements, E) or isinstance(elements, Element):
            self.elements.append(elements)
        else:
            self.elements += elements
        return self

    def __enter__(self):
        """
        Makes a layer usable in a with statement:
        with arviz.stage("MyLayer") as layer:
            layer.elements += [ ... ]
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
