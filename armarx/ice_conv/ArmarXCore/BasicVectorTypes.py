import numpy as np

from typing import List, Optional, Union

from armarx.ice_conv.ice_converter import IceConverter


SLICE_INCLUDE = ("ArmarXCore", "core/BasicVectorTypes.ice")


def import_vector2f():
    load_armarx_slice(*SLICE_INCLUDE)
    import armarx
    return armarx.Vector2f


def import_vector3f():
    load_armarx_slice(*SLICE_INCLUDE)
    import armarx
    return armarx.Vector3f


class Vector2fConv(IceConverter):

    def __init__(self):
        super().__init__()
        self.set_handler_from_ice(list, self._from_ice)
        self.set_handler_to_ice(np.ndarray, self._to_ice)


    def _from_ice(
            self,
            dto: Union["armarx.Vector2f", List["armarx.Vector2f"]],
            scaling: Optional[float] = None,
            ) -> np.ndarray:

        if isinstance(dto, list):
            points = dto
            bo = np.array([(p.e0, p.e1) for p in points])
            assert bo.shape == (len(points), 2), \
                "Shape should be {}, but was {}.\n\tPoints: {}".format((len(points), 2), bo.shape, points)
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
        Vector2f = import_vector2f()

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


    def _from_ice(
            self,
            dto_points: List["armarx.Vector2f"],
            scaling: Optional[float] = None,
            ) -> np.ndarray:

        bo = np.array([(p.e0, p.e1, p.e2) for p in dto_points])
        assert bo.shape == (len(dto_points), 3), \
            "Shape should be {}, but was {}.\n\tPoints: {}".format((len(dto_points), 3), bo.shape, dto_points)

        bo = scale(bo, scaling)
        return bo


    def _to_ice(
            self,
            bo: np.ndarray,
            scaling: Optional[float] = None,
            ) -> "armarx.Vector3f":
        Vector3f = import_vector3f()

        bo = scale(bo, scaling)

        if bo.ndim == 1:
            x, y, z = bo
            return Vector3f(x, y, z)
        else:
            return [Vector3f(x, y, z) for x, y, z in bo]



def scale(points: np.ndarray, scaling: Optional[float] = None) -> np.ndarray:
    return points if scaling is None else points * scaling