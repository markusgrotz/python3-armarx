#!/usr/bin/env python3

import logging
import math

import numpy as np

from armarx_core import ice_manager
from armarx_core.tools.metronome import Metronome
from armarx_core.parser import ArmarXArgumentParser
from armarx_memory import client as amc
from armarx_memory import core as amcore
from armarx_memory.aron.conversion import pythonic_from_to_aron_ice

log = logging.getLogger(__name__)

WIDTH = 160
HEIGHT = 120


def make_point_cloud(time_usec: int):
    # The point type will be derived from the fields in the dtype.
    # Padding required to match the PCL byte alignment will be added automatically.
    # However, the order of the fields must match the PCL definition.
    # Note: Colors of PCL point clouds are encoded as BGRA.
    dtype = np.dtype([("position", np.float32, (3,)), ("color", np.uint32)])

    point_cloud = np.zeros((WIDTH, HEIGHT), dtype=dtype)

    # You can slice the relevant data fields out of the structured data
    positions = point_cloud[
        "position"
    ]  # This is a view to the position data (3D array float32)
    colors = point_cloud[
        "color"
    ]  # This is a view to the color data (1D array of uint32)

    for y in range(HEIGHT):
        py = 2.0 * y
        phase = (time_usec / 1e6) + py / 50.0
        height_t = max(0.0, min(0.5 * (1.0 + math.sin(phase)), 1.0))

        for x in range(WIDTH):
            g = int(255.0 * height_t)
            b = int(255 * (1.0 - height_t))
            r = 255

            colors[x, y] = b + (g * 256) + (r * 256 * 256)

            point = positions[x, y]
            point[0] = x
            point[1] = y
            point[2] = 50 * height_t

    return point_cloud


def main():
    name = "point_clouds_to_memory_example"

    point_cloud_entity_id = amc.MemoryID(
        memory_name="Vision",
        core_segment_name="PointCloudXYZRGBA",
        provider_segment_name=name,
        entity_name="example",
    )

    mns = amc.MemoryNameSystem.wait_for_mns()
    writer = mns.wait_for_writer(point_cloud_entity_id)

    logged_once = False

    try:
        metronome = Metronome(frequency_hertz=30)

        while ice_manager.is_alive():
            metronome.wait_for_next_tick()

            time_usec = amcore.time_usec()

            point_cloud = make_point_cloud(time_usec)

            if not logged_once:
                log.info(f"Commit first point cloud with shape {point_cloud.shape} ...")
                logged_once = True

            # Construct your result (should match the memory segment type).
            data = {
                "pointcloud": point_cloud,
            }
            data_aron_ice = pythonic_from_to_aron_ice.pythonic_to_aron_ice(data)

            commit = amc.Commit()
            commit.add(amc.EntityUpdate(
                entity_id=point_cloud_entity_id,
                instances_data=[data_aron_ice],
                time_referenced_usec=time_usec,
            ))

            writer.commit(commit)

    except KeyboardInterrupt:
        log.info("Shutting down.")


if __name__ == "__main__":
    parser = ArmarXArgumentParser()
    args = parser.parse_args()

    main()
