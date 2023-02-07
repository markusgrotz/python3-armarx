from typing import List, Union, Tuple, Any

import numpy as np

from armarx.viz.data import Element


import armarx.viz as viz

from armarx.arviz import conversions as conv
from .Element import Element


class Mesh(Element):
    """
    A 3D mesh made of triangular faces.

    A mesh is specified by:

    * an array `vertices` of 3D vertex positions (x, y, z) with shape (V, 3),
    * an array `colors` of colors (r, g, b) or (r, g, b, a) with shape (C, 3) or (C, 4), and
    * an array `faces` of shape (F, 6), where each entry (v1, v2, v3, c1, c2, c3) specifies
      the indices of the three adjacent vertices (indexing the `vertices` array) and indices
      of adjacent vertex colors (indexing the `colors` array).

    """

    def __init__(
        self,
        id,
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementMesh, id=id, **kwargs)

        self.vertices = []
        self.colors = []
        self.faces = []

    @property
    def vertices(self) -> np.ndarray:
        """An N x 3 array of vertex positions."""
        assert self._match_shapes(
            self._vertices.shape, [(0,), (None, 3)]
        ), self._vertices.shape
        return self._vertices

    @vertices.setter
    def vertices(self, value):
        value = self._to_array_checked(
            value, [(0,), (None, 3)], "mesh vertices", dtype=np.float
        )
        self._vertices = value

    @property
    def colors(self):
        """An N x 4 array of vertex colors."""
        assert self._match_shapes(
            self._colors.shape, [(0,), (None, 4)]
        ), self._colors.shape
        return self._colors

    @colors.setter
    def colors(self, value):
        value = self._to_array_checked(
            value, [(0,), (None, 3), (None, 4)], "mesh colors", dtype=np.float
        )
        if value.shape[-1] == 3:
            self._colors = np.concatenate([value, [[255]] * len(value)], axis=-1)
        else:
            self._colors = value

    @property
    def faces(self) -> np.ndarray:
        """
        An N x 6 array of vertex position and color indices.
        An entry has the form:
        [ v0 v1 v2 c0 c1 c2 ]
        """
        assert self._match_shapes(self._faces.shape, [(0,), (None, 6)])
        return self._faces

    @faces.setter
    def faces(self, value: Union[np.ndarray, List[viz.data.Face]]):
        value = self._to_array_checked(
            value, [(0,), (None, 6)], "mesh faces", dtype=int
        )
        self._faces = value

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)

        ice_data.vertices = conv.vector3fs_from_numpy(self.vertices)
        ice_data.colors = [conv.to_viz_color(c) for c in self.colors]
        ice_data.faces = [viz.data.Face(*map(int, f)) for f in self.faces]

    @staticmethod
    def make_grid2d_faces(
        num_x: int,
        num_y: int,
    ) -> np.ndarray:
        """
        Make vertex and color indices of triangular faces of a 2D grid.

        Note that the vertex and color indices are independent of concrete
        vertex positions and color values. They merely state which vertices
        are connected to triangular faces and which color each vertex (in each
        face) has. The vertex positions and color values are specified by
        the `vertices` and `colors` arrays.

        Indices created by this function match the order of vertices
        produced by `armarx.arviz.grids.make_grid()` and related functions.

        :param num_x:
            The number of vertices in first dimension.
        :param num_y:
            The number of vertices in second dimension.
        :return:
            An array f of shape (num_faces, 3+3) with f[i] = (v1, v2, v3, c1, c2, c3)
            are the vertex and color indices of a triangular face.
        """
        num_faces = 2 * (num_x - 1) * (num_y - 1)
        faces = np.zeros((num_faces, 6))

        i = 0
        for x in range(num_x - 1):
            for y in range(num_y - 1):
                """
                In counter-clockwise order:
                      (x)  (x+1)
                 (y)   *----*
                       | \f1|
                       |f2\ |
                 (y+1) *----*
                """
                v0 = c0 = y * num_x + x
                v1 = c1 = (y + 1) * num_x + (x + 1)
                v2 = c2 = (y + 1) * num_x + x
                faces[i] = v0, v1, v2, c0, c1, c2
                i += 1

                v0 = c0 = y * num_x + x
                v1 = c1 = y * num_x + (x + 1)
                v2 = c2 = (y + 1) * num_x + (x + 1)
                faces[i] = v0, v1, v2, c0, c1, c2
                i += 1

        assert i == num_faces

        return faces
