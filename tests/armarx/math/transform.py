import pytest

import numpy as np
from transforms3d.axangles import axangle2mat

from armarx_core.math.transform import Transform


@pytest.fixture
def element() -> Transform:
    e = Transform(translation=(10, 20, 30), rotation=axangle2mat((0, 0, 1), np.pi / 2))
    return e


def test_default_identity():
    identity = Transform()
    assert np.allclose(identity.transform, np.eye(4))


def test_ctor_translation_only():
    identity = Transform(translation=(10, 20, 30))
    assert np.allclose(identity.translation, (10, 20, 30))
    assert np.allclose(identity.rot_mat, np.eye(3))
    assert identity.transform.shape == (4, 4)


def test_ctor_rotation_only():
    identity = Transform(rotation=axangle2mat((0, 0, 1), np.pi))
    expected = [[-1, 0, 0], [0, -1, 0], [0, 0, 1]]
    assert np.allclose(identity.rot_mat, expected)
    assert np.allclose(identity.translation, np.zeros(3))
    assert identity.transform.shape == (4, 4)


def test_rotation_roundtrip(element: Transform):
    original_mat = element.rot_mat
    element.rot_quat = element.rot_quat
    assert np.allclose(element.rot_mat, original_mat)


def test_mul_identity(element: Transform):
    identity = Transform()

    product = element * identity
    assert product.is_close_to(element)

    product = identity * element
    assert product.is_close_to(element)


def test_mul_rotate_translation():
    a = Transform(rotation=axangle2mat((0, 0, 1), np.pi))
    b = Transform(translation=(10, 20, 30))

    result = a * b
    expected = Transform(
        translation=(-10, -20, 30), rotation=axangle2mat((0, 0, 1), np.pi)
    )

    assert result.is_close_to(expected)


def test_inverted(element: Transform):
    inverted = element.inverted()
    product = inverted * element
    assert product.is_close_to(Transform())

    product = element * inverted
    assert product.is_close_to(Transform())
