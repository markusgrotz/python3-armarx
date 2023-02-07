import numpy as np

from typing import List, Tuple, Union

from armarx import remote_gui as rg


class NdArrayWidget:
    """
    A grid of float or int spin boxes parametrizing a 1D or 2D numpy array.
    """

    SpinBox = Union[rg.FloatSpinBox, rg.IntSpinBox]

    def __init__(
        self,
        array: np.ndarray,
        column_vector=False,
        float_widget_cls=rg.FloatSpinBox,
        int_widget_cls=rg.IntSpinBox,
        **kwargs,
    ):
        array = np.array(array)

        if "row_vector" in kwargs:
            print(
                "NdArrayWidget(): The argument 'row_vector' was replaced by 'column_vector'.\n"
                "If you are using 'row_vector=True', use 'column_vector=False' instead, and vice-versa."
            )
            column_vector = not kwargs.pop("row_vector")

        if "int" in array.dtype.name:
            self.spin_box_type = int_widget_cls
            self.scalar_type = int
        else:
            self.spin_box_type = float_widget_cls
            self.scalar_type = float

        self.column_vector = column_vector
        self.spin_boxes = np.zeros(array.shape, dtype=np.object)
        for i in range(self.spin_boxes.size):
            sb = self.spin_box_type(value=self.scalar_type(array.flat[i]), **kwargs)
            self.spin_boxes.flat[i] = sb

    def create_tree(
        self,
    ):
        layout = rg.GridLayout()
        if self.spin_boxes.ndim == 1:
            for i, sb in enumerate(self.spin_boxes):
                layout.add(sb, (i, 0) if self.column_vector else (0, i))

        elif self.spin_boxes.ndim == 2:
            for i, row in enumerate(self.spin_boxes):
                for j, sb in enumerate(row):
                    layout.add(sb, (i, j))
        else:
            raise ValueError(
                f"{self.__class__.__name__} supports only 1- and 2-dimensional arrays, "
                f"but requested ndim is {self.spin_boxes.ndim}."
            )
        return layout

    @property
    def value(self) -> np.ndarray:
        array = np.zeros(self.spin_boxes.shape, dtype=self.scalar_type)
        for i in range(self.spin_boxes.size):
            array.flat[i] = self.spin_boxes.flat[i].value
        return array

    @value.setter
    def value(self, values: np.ndarray):
        assert (
            values.shape == self.spin_boxes.shape
        ), f"Shape mismatch (expected {self.spin_boxes.shape}, but got {values.shape})."

        for sb, val in zip(self.spin_boxes.flat, values.flat):
            sb.value = self.scalar_type(val)

    def get_array(
        self,
    ) -> np.ndarray:
        return self.value

    def has_any_changed(self):
        for sb in self.spin_boxes.flat:
            if sb.has_value_changed():
                return True
        return False

    def find_changed(self) -> List[Tuple]:
        indices = np.indices(self.spin_boxes.shape).T.reshape(-1, self.spin_boxes.ndim)
        return [
            tuple(i) for i in indices if self.spin_boxes[tuple(i)].has_value_changed()
        ]
