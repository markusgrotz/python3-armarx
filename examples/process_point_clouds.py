#!/usr/bin/env python3

import logging
import numpy as np

from armarx.ice_manager import is_alive
from visionx.pointcloud_receiver import PointCloudReceiver
from visionx.pointcloud_provider import PointCloudProvider, dtype_point_color_xyz

logger = logging.getLogger(__name__)


def main():
    receiver = PointCloudReceiver("ExamplePointCloudReceiver", source_provider_name="OpenNIPointCloudProvider")
    receiver.on_connect()

    result_provider = PointCloudProvider("ExamplePointCloudResult", point_dtype=dtype_point_color_xyz, connect=True)
    # on_connect is called in the constructor if connect=True
    # result_provider.on_connect()

    try:
        while is_alive():
            pc, info = receiver.wait_for_next_point_cloud()

            # The point cloud we get is read-only, so we need to copy before modifying
            new_pc = np.copy(pc)

            # Change the color of some points
            y_mask = pc['position'][:,1] > 0.0
            new_pc['color'][y_mask] = 255
            new_pc['color'][np.logical_not(y_mask)] = 255*256

            z_mask = pc['position'][:,2] > 3000.0
            new_pc['color'][z_mask] += 255*256*256

            result_provider.update_point_cloud(new_pc)

    except KeyboardInterrupt:
        logger.info('shutting down')
    finally:
        result_provider.on_disconnect()
        receiver.on_disconnect()


if __name__ == '__main__':
    main()
