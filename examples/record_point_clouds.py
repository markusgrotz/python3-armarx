import datetime
import logging
import os.path

import numpy as np

from armarx.ice_manager import is_alive
from visionx.pointcloud_processor import PointCloudReceiver

logger = logging.getLogger(__name__)

output_directory = os.path.expandvars("$HOME/recorded-point-clouds")

name = "PointCloudRecorder"
source_provider_name = (
    # "OpenNIPointCloudProvider"
    "DynamicSimulationDepthImageProvider"
)

max_fps = 30


def main():
    receiver = PointCloudReceiver(name=name, source_provider_name=source_provider_name)

    logger.info(f"Wait for point cloud provider '{receiver.source_provider_name}' ...")
    receiver.on_connect(wait_for_provider=True)

    t_start = datetime.datetime.now()
    t_latest = None
    count = 0

    directory = os.path.join(output_directory, str(t_start))
    logger.info(f"Storing point clouds in '{directory}'.")
    os.makedirs(directory, exist_ok=True)

    try:
        while is_alive():
            pc, info = receiver.wait_for_next_point_cloud()
            now = datetime.datetime.now()

            if t_latest is not None and (now - t_latest).total_seconds() < (1 / max_fps):
                continue
            else:
                t_latest = now

            # The point cloud we get is read-only, so we need to copy before modifying.
            new_pc: np.ndarray = np.copy(pc)

            filename = f"pointcloud_{now - t_start}.npy"
            filepath = os.path.join(directory, filename)

            np.save(filepath, new_pc)
            count += 1

            print_step = 10 ** max(1, int(np.log10(count)))
            if count % print_step == 0:
                logger.info(f"Stored {count} point clouds (reporting each {print_step}) ...")


    except KeyboardInterrupt:
        logger.info("Shutting down.")
    finally:
        # result_provider.on_disconnect()
        receiver.on_disconnect()


if __name__ == '__main__':
    main()
