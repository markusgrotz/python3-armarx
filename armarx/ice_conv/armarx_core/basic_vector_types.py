import numpy as np

from typing import List, Optional, Union

import armarx
from armarx import slice_loader
from armarx_memory.ice_conv.ice_converter import IceConverter

SLICE_INCLUDE = ("ArmarXCore", "core/BasicVectorTypes.ice")


class Vector2fConv(IceConverter):
    def __init__(self):
        super().__init__()
        self.set_handler_from_ice(list, self._from_ice)
        self.set_handler_to_ice(np.ndarray, self._to_ice)

    def _import_dto(cls):
        slice_loader.load_armarx_slice(*SLICE_INCLUDE)
        return armarx.Vector2f

    def _from_ice(
        self,
        dto: Union["armarx.Vector2f", List["armarx.Vector2f"]],
        scaling: Optional[float] = None,
    ) -> np.ndarray:

        if isinstance(dto, list):
            points = dto
            bo = np.array([(p.e0, p.e1) for p in points])
            assert bo.shape == (
                len(points),
                2,
            ), "Shape should be {}, but was {}.\n\tPoints: {}".format(
                (len(points), 2), bo.shape, points
            )
        else:
            point = dto
            bo = np.array((point.e0, point.e1))

        bo = scale(bo, scaling)
        return bo

    def _to_ice(
        self,
        bo: np.ndarray,
        scaling: Optional[float] = None,
    ) -> "armarx.Vector2f":
        Vector2f = self.get_dto()

        bo = np.array(bo)
        bo = scale(bo, scaling)

        if bo.ndim == 1:
            x, y = bo
            return Vector2f(x, y)
        else:
            return [Vector2f(x, y) for x, y in bo]


class Vector3fConv(IceConverter):
    def __init__(self):
        super().__init__()
        self.set_handler_from_ice(list, self._from_ice)
        self.set_handler_to_ice(np.ndarray, self._to_ice)

    def _import_dto(cls):
        slice_loader.load_armarx_slice(*SLICE_INCLUDE)
        return armarx.Vector3f

    def _from_ice(
        self,
        dto_points: Union["armarx.Vector3f", List["armarx.Vector3f"]],
        scaling: Optional[float] = None,
    ) -> np.ndarray:

        try:
            iter(dto_points)
        except TypeError:
            p = dto_points
            bo = np.array([p.e0, p.e1, p.e2])

        else:
            bo = np.array([(p.e0, p.e1, p.e2) for p in dto_points])
            assert bo.shape == (
                len(dto_points),
                3,
            ), "Shape should be {}, but was {}.\n\tPoints: {}".format(
                (len(dto_points), 3), bo.shape, dto_points
            )

        bo = scale(bo, scaling)
        return bo

    def _to_ice(
        self,
        bo: np.ndarray,
        scaling: Optional[float] = None,
    ) -> "armarx.Vector3f":
        Vector3f = self.get_dto()

        bo = scale(bo, scaling)

        if bo.ndim == 1:
            x, y, z = bo
            return Vector3f(x, y, z)
        else:
            return [Vector3f(x, y, z) for x, y, z in bo]


def scale(points: np.ndarray, scaling: Optional[float] = None) -> np.ndarray:
    points = np.array(points)
    return points if scaling is None else points * scaling
