#!/usr/bin/env python3

import logging
import math

import numpy as np

from armarx_core import ice_manager
from armarx_core.tools.metronome import Metronome
from armarx_core.parser import ArmarXArgumentParser
from armarx_memory import client as amc
from armarx_memory import core as amcore

logger = logging.getLogger(__name__)

WIDTH = 160
HEIGHT = 120


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


    dtype = np.dtype([("position", np.float32, (3,)), ("color", np.uint32)])

    try:
        metronome = Metronome(frequency_hertz=30)

        while ice_manager.is_alive():
            metronome.wait_for_next_tick()

            pc = np.zeros((WIDTH, HEIGHT), dtype=dtype)

            time_usec = amcore.time_usec()

            # You can slice the relevant data fields out of the structured data
            positions = pc[
                "position"
            ]  # This is a view to the position data (3D array float32)
            colors = pc[
                "color"
            ]  # This is a view to the color data (1D array of uint32)

            index = 0
            for y in range(HEIGHT):
                py = 2.0 * y
                phase = (time_usec / 1e6) + py / 50.0
                height_t = max(0.0, min(0.5 * (1.0 + math.sin(phase)), 1.0))
                for x in range(WIDTH):
                    g = int(255.0 * height_t)
                    b = int(255 * (1.0 - height_t))
                    colors[index] = 255 + g * 256 + b * 256 * 256
                    # The following code is very slow and is therefore commented out
                    # colors[index] = rgb_to_uint32(255, g, b)
                    point = positions[index]
                    point[0] = x
                    point[1] = y
                    point[2] = 50 * height_t

                    index += 1

            data = {
                "pointcloud": point_cloud_entity_id,
            }

            commit = amc.Commit()
            commit.add(amc.EntityUpdate(
                entity_id=point_cloud_entity_id,
                instances_data=[data],
                time_referenced_usec=time_usec,
            ))

            writer.commit(commit)

    except KeyboardInterrupt:
        logger.info("Shutting down.")


if __name__ == "__main__":
    parser = ArmarXArgumentParser()
    args = parser.parse_args()

    main()
