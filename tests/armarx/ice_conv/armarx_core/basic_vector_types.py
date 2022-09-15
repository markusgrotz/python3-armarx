import pytest

import numpy as np
from armarx import slice_loader
from armarx.ice_conv.armarx_core import basic_vector_types as conv

slice_loader.load_armarx_slice("ArmarXCore", "core/BasicVectorTypes.ice")
from armarx import Vector2f, Vector3f

conv2f = conv.Vector2fConv()
conv3f = conv.Vector2fConv()


def test_vector2f_from_ice_single():
    bo: np.ndarray = conv2f.from_ice(Vector2f(2.0, -6.0))
    assert isinstance(bo, np.ndarray)
    assert bo.shape == (2,)
    assert bo.dtype == np.float64
    assert bo[0] == 2.0
    assert bo[1] == -6.0


def test_vector2f_from_ice_multiple():
    bo: np.ndarray = conv2f.from_ice(
        [Vector2f(2.0, -6.0), Vector2f(3.0, -7.0), Vector2f(4.0, -8.0)]
    )
    assert isinstance(bo, np.ndarray)
    assert bo.shape == (
        3,
        2,
    )
    assert bo.dtype == np.float64
    assert bo[0, 0] == 2.0
    assert bo[0, 1] == -6.0
    assert bo[1, 0] == 3.0
    assert bo[1, 1] == -7.0
    assert bo[2, 0] == 4.0
    assert bo[2, 1] == -8.0


def test_vector2f_to_ice_single():
    dto: np.ndarray = conv2f.to_ice(np.array((2.0, -6.0)))
    assert isinstance(dto, Vector2f)
    assert dto.e0 == 2.0
    assert dto.e1 == -6.0


def test_vector2f_to_ice_multiple():
    dto = conv2f.to_ice(np.array([(2.0, -6.0), (3.0, -7.0), (4.0, -8.0)]))
    assert isinstance(dto, list)
    assert len(dto) == 3
    assert dto[0].e0 == 2.0
    assert dto[0].e1 == -6.0
    assert dto[1].e0 == 3.0
    assert dto[1].e1 == -7.0
    assert dto[2].e0 == 4.0
    assert dto[2].e1 == -8.0
