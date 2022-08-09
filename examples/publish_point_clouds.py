#!/usr/bin/env python3

import logging
import time
import math

from armarx.ice_manager import is_alive
from armarx.parser import ArmarXArgumentParser as ArgumentParser
from visionx.pointclouds import rgb_to_uint32
from visionx.pointcloud_provider import PointCloudProvider
from visionx.pointcloud_provider import dtype_point_color_xyz

logger = logging.getLogger(__name__)

WIDTH = 160
HEIGHT = 120


def main():
    pc_provider = PointCloudProvider('ExamplePointCloudProvider', point_dtype=dtype_point_color_xyz,
                                     initial_capacity=WIDTH * HEIGHT)
    pc_provider.on_connect()

    try:
        while is_alive():
            pc = pc_provider.create_point_cloud_array(WIDTH * HEIGHT)
            t = time.time()

            # You can slice the relevant data fields out of the structured data
            positions = pc['position']  # This is a view to the position data (3D array float32)
            colors = pc['color']  # This is a view to the color data (1D array of uint32)

            index = 0
            for y in range(HEIGHT):
                py = 2.0 * y
                phase = t + py / 50.0
                height_t = max(0.0, min(0.5 * (1.0 + math.sin(phase)), 1.0))
                for x in range(WIDTH):
                    g = int(255.0 * height_t)
                    b = int(255 * (1.0 - height_t))
                    colors[index] = 255 + g*256 + b*256*256
                    # The following code is very slow and is therefore commented out
                    # colors[index] = rgb_to_uint32(255, g, b)
                    point = positions[index]
                    point[0] = x
                    point[1] = y
                    point[2] = 50 * height_t

                    index += 1
                    
            pc_provider.update_point_cloud(pc)
            time.sleep(1e-3)

    except KeyboardInterrupt:
        logger.info('shutting down')


if __name__ == '__main__':
    parser = ArgumentParser()
    args = parser.parse_args()

    main()
