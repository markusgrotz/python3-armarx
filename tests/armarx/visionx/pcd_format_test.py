import os
import pytest

import numpy as np

import visionx.pointclouds as vpc


def test_store_and_load_pcd_file():
    filepath = "test.pcd"

    pc = np.zeros((10, 20), dtype=vpc.dtype_point_color_xyz)

    for i in range(pc.shape[0]):
        for j in range(pc.shape[1]):
            pc["position"][i, j] = (i, j, -i * j)
            pc["color"][i, j] = vpc.rgb_to_uint32(*(50 + 10 * np.array([i, j, -i * j])))

    vpc.store_point_cloud(filepath, pc)
    assert os.path.isfile(filepath)

    loaded = vpc.load_point_cloud(filepath)
    assert loaded.shape == pc.shape
    assert loaded.dtype == pc.dtype

    assert set(loaded.dtype.names) == {"position", "color"}
    for field in pc.dtype.names:
        assert np.array_equal(loaded[field], pc[field], equal_nan=True)

    os.remove(filepath)
    assert not os.path.exists(filepath)
