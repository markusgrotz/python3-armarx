import numpy as np

from typing import List, Tuple, Union, Callable, Any

from armarx.arviz.elements import Box
from armarx.arviz.layer import Layer
from armarx.arviz.volumetric.size_models import SizeModel, FixedScaleSizeModel


def get_grid_coordinates(
    bounds: Union[np.ndarray, List[Tuple[float, float]]],
    num=None,
    flatten_dims=True,
    return_voxel_size=False,
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """
    Create coordinates in a 3D grid.

    The coordinates of a single point form the last axis.

    :param bounds:
        Limits in the form [(x0, x1), (y0, y1), (z0, z1)] (shape (d, 2))
        or [(x0, y0, z0), (x1, y1, z1)] (shape (2, d)).
    :param num:
        Number grid coordinates along each axis.
    :param flatten_dims:
        If true (default), the resulting array has shape (num^d, d),
        otherwise it has (num, num, num, d).
    :param return_voxel_size:
        If true, return the extents of a single voxel element, i.e.
        the 3D offset between two grid coordinates.

    :return: The grid coordinates with a the last axis representing a single point.
    """
    num = num or 16

    bounds = np.array(bounds)
    if bounds.ndim != 2:
        raise ValueError(f"Bounds must be 2D, but shape was {bounds.shape}.")
    if bounds.shape[-1] != 2 and bounds.shape[0] == 2:
        bounds = bounds.T

    xs = np.stack(np.meshgrid(*[np.linspace(a, b, num) for a, b in bounds]))
    xs = np.moveaxis(xs, 0, -1)
    voxel_size = xs[1, 1, 1] - xs[0, 0, 0]

    if flatten_dims:
        xs = xs.reshape(-1, len(bounds))

    if return_voxel_size:
        return xs, voxel_size
    else:
        return xs


class Volumetric:
    def __init__(
        self,
        bounds,
        num=None,
        alpha=None,
        cmap=None,
        size_model: SizeModel = None,
    ):

        self.bounds = bounds
        self.num = num or 16

        self.alpha = alpha

        if cmap is None:
            from matplotlib.cm import get_cmap

            cmap = get_cmap("viridis")
        elif isinstance(cmap, str):
            from matplotlib.cm import get_cmap

            cmap = get_cmap(cmap)
        self.cmap = cmap

        self.size_model = size_model or FixedScaleSizeModel(scale=1.0)
        self._size_model_context = SizeModel.Context()

    def draw_on(
        self,
        func: Callable[[Any], np.ndarray],
        layer: Layer,
        vlimits=None,
        id_prefix="",
    ):
        import matplotlib.pyplot as plt

        xs, voxel_size = get_grid_coordinates(
            self.bounds, self.num, return_voxel_size=True
        )
        ys = np.array(func(xs))

        if vlimits is None:
            vlimits = (ys.min(), ys.max())

        normalize = plt.Normalize(vmin=vlimits[0], vmax=vlimits[1])
        colors = self.cmap(normalize(ys))
        colors = (colors * 255).astype(np.int)
        if self.alpha is not None:
            colors[:, -1] = self.alpha

        self.size_model.set_value_limits(vlimits[0], vlimits[1])

        for i, (x, y, color) in enumerate(zip(xs, ys, colors)):
            self._size_model_context.i = i
            self._size_model_context.x = x
            self._size_model_context.y = y

            size = self.size_model.get_size(
                voxel_size=voxel_size, context=self._size_model_context
            )
            if size is None or min(size) <= 0:
                continue
            layer.add(Box(f"{id_prefix}{i:>04}", position=x, size=size, color=color))
