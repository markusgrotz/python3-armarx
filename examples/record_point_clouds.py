import datetime
import logging
import os.path
import time

import numpy as np

from armarx.ice_manager import is_alive
from visionx.pointcloud_processor import PointCloudReceiver
from visionx.pointcloud_provider import PointCloudProvider, dtype_point_color_xyz

logger = logging.getLogger(__name__)


output_directory = os.path.expandvars("$HOME/recorded-point-clouds")


def main():
    name = "PointCloudRecorder"
    receiver = PointCloudReceiver(name, source_provider_name="OpenNIPointCloudProvider")
    receiver.on_connect()

    # result_provider = PointCloudProvider(f"{name}Result", point_dtype=dtype_point_color_xyz, connect=True)
    # on_connect is called in the constructor if connect=True
    # result_provider.on_connect()

    start = datetime.datetime.now()
    try:
        while is_alive():
            pc, info = receiver.wait_for_next_point_cloud()

            # The point cloud we get is read-only, so we need to copy before modifying
            new_pc: np.ndarray = np.copy(pc)

            delta = datetime.datetime.now() - start
            filename = f"pointcloud_{delta}.npy"
            filepath = os.path.join(output_directory, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            np.save(new_pc)

    except KeyboardInterrupt:
        logger.info("Shutting down.")
    finally:
        # result_provider.on_disconnect()
        receiver.on_disconnect()


if __name__ == '__main__':
    main()
