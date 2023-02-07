import abc

import numpy as np

from typing import List, Tuple, Union, Callable, Any, Optional

from armarx.math import rescale


class SizeModel(abc.ABC):
    class Context:
        def __init__(self, i=0, x=0.0, y=0.0):
            self.i = i
            self.x = x
            self.y = y

    def __init__(self):
        pass

    @abc.abstractmethod
    def get_size(
        self,
        voxel_size: np.ndarray,
        c: Context,
    ) -> Optional[np.ndarray]:
        pass

    def set_value_limits(
        self,
        vmin: float,
        vmax: float,
    ):
        pass


class FixedScaleSizeModel(SizeModel):
    def __init__(self, scale=1.0):
        super().__init__()
        self.scale = scale

    def get_size(self, voxel_size, context):
        return self.scale * voxel_size


class ValueProportionalSizeModel(SizeModel):
    """
    Size model that scales voxel proportionally to their value.
    """

    def __init__(
        self,
        from_lo_t=0.0,
        from_hi_t=1.0,
        to_lo_scale=0.0,
        to_hi_scale=1.0,
        fixed_scale=1.0,
        value_limits=(0.0, 1.0),
        min_absolute_size=1e-4,
    ):
        super().__init__()

        self.from_lo_t = from_lo_t
        self.from_hi_t = from_hi_t
        self.to_lo_scale = to_lo_scale
        self.to_hi_scale = to_hi_scale
        self.fixed_scale = fixed_scale

        self.from_lo = 0.0
        self.from_hi = 1.0
        self.set_value_limits(value_limits[0], value_limits[1])

        self.min_absolute_size = min_absolute_size

    def set_value_limits(self, vmin: float, vmax: float):
        self.from_lo = rescale(self.from_lo_t, 0.0, 1.0, vmin, vmax)
        self.from_hi = rescale(self.from_hi_t, 0.0, 1.0, vmin, vmax)

    def get_size(self, voxel_size, context):
        prop = rescale(
            context.y,
            from_lo=self.from_lo,
            from_hi=self.from_hi,
            to_lo=self.to_lo_scale,
            to_hi=self.to_hi_scale,
            clip=True,
        )
        size = prop * self.fixed_scale * voxel_size
        return size if min(size) > self.min_absolute_size else np.zeros_like(size)
