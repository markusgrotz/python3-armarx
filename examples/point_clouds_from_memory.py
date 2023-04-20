#!/usr/bin/env python3

import logging

import numpy as np
import typing as ty

from armarx_core.parser import ArmarXArgumentParser
from armarx_memory import client as amc

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    parser = ArmarXArgumentParser()
    args = parser.parse_args()

    point_cloud_entity_id = amc.MemoryID(
        memory_name="Vision",
        core_segment_name="PointCloudXYZRGBA",
        provider_segment_name="PointCloudToArMem",
        entity_name="PointCloud",
    )

    mns = amc.MemoryNameSystem.wait_for_mns()
    reader = mns.wait_for_reader(point_cloud_entity_id)

    query_result = reader.query_latest(point_cloud_entity_id)

    def process_instance(id_: amc.MemoryID, data: ty.Dict):
        return data

    instances_data = reader.for_each_instance_data(process_instance, query_result)
    instance_data: ty.Dict = instances_data[0]

    point_cloud = instance_data["pointcloud"]

    logger.info(f"Point cloud (shape {point_cloud.shape}): \n{point_cloud}")
    logger.info("Available fields:\n  " + ", ".join(point_cloud.dtype.fields))

    positions = point_cloud["position"]
    assert positions.dtype == np.float32
    assert positions.shape[-1] == 3
    logger.info(f"Positions (shape {positions.shape}): {repr(positions)}")
