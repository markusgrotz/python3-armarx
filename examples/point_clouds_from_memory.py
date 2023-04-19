#!/usr/bin/env python3

import logging

import numpy as np
import typing as ty

from armarx_core.parser import ArmarXArgumentParser
# from visionx.pointcloud_receiver import PointCloudReceiver
# from visionx.pointcloud_provider import PointCloudProvider, dtype_point_color_xyz

from armarx_memory import aron
from armarx_memory import client as amc


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    parser = ArmarXArgumentParser()
    args = parser.parse_args()

    point_cloud_entity_id = amc.MemoryID(
        "Vision",
        "PointCloudXYZRGBA",
        "PointCloudToArMem",
        "PointCloud",
    )

    mns = amc.MemoryNameSystem.wait_for_mns()
    reader = mns.wait_for_reader(point_cloud_entity_id)

    query_result = reader.query_latest(point_cloud_entity_id)

    def process_instance(id_: amc.MemoryID, data: ty.Dict):
        return data

    # instance_data: ty.Dict
    [instances_data] = reader.for_each_instance_data(process_instance, query_result)

    point_cloud = instances_data["pointcloud"]

    print(f"Point cloud (shape {point_cloud.shape}): \n{point_cloud}")
    print("Available fields:\n  " + ", ".join(point_cloud.dtype.fields))

    positions = point_cloud["position"]
    assert positions.dtype == np.float32
    assert positions.shape[-1] == 3
    print(f"Positions (shape {positions.shape}): {repr(positions)}")
