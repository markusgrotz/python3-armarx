import datetime
import logging
import os.path

import numpy as np

from armarx.ice_manager import is_alive
from visionx.pointcloud_processor import PointCloudReceiver

logger = logging.getLogger(__name__)


class PointCloudRecorder:

    def __init__(
            self,
            output_directory: str,
            source_provider_name: str,
            name = "PointCloudRecorder",
            max_fps=30,
    ):
        self.output_directory = output_directory
        self.source_provider_name = source_provider_name
        self.name = name
        self.max_fps = max_fps

        # Init receiver.
        self.receiver = PointCloudReceiver(name=name, source_provider_name=source_provider_name)
        logger.info(f"Wait for point cloud provider '{self.receiver.source_provider_name}' ...")
        self.receiver.on_connect(wait_for_provider=True)


        # Prepare replay.
        self.t_start = datetime.datetime.now()
        self.t_latest = None
        self.count = 0

        # Prepare output dir.
        self.directory = os.path.join(output_directory, str(self.t_start))
        logger.info(f"Storing point clouds in '{self.directory}'.")
        os.makedirs(self.directory, exist_ok=True)

    def disconnect(self):
        self.receiver.on_disconnect()

    def record_once(self):
        pc, info = self.receiver.wait_for_next_point_cloud()
        now = datetime.datetime.now()

        if self.t_latest is not None and (now - self.t_latest).total_seconds() < (1 / self.max_fps):
            return
        else:
            self.t_latest = now

        # The point cloud we get is read-only, so we need to copy before modifying.
        new_pc: np.ndarray = np.copy(pc)

        filename = f"pointcloud_{now - self.t_start}.npy"
        filepath = os.path.join(self.directory, filename)

        np.save(filepath, new_pc)
        self.count += 1

        print_step = 10 ** max(1, int(np.log10(self.count)))
        if self.count % print_step == 0:
            logger.info(f"Stored {self.count} point clouds (reporting each {print_step}) ...")


def main():

    recorder = PointCloudRecorder(
        output_directory=os.path.expandvars("$HOME/recorded-point-clouds"),
        # source_provider_name="OpenNIPointCloudProvider",
        source_provider_name="DynamicSimulationDepthImageProvider",
    )

    try:
        while is_alive():
            recorder.record_once()

    except KeyboardInterrupt:
        logger.info("Shutting down.")

    finally:
        recorder.disconnect()


if __name__ == '__main__':
    main()
