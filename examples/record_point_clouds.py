#!/usr/bin/env python3

import datetime
import logging
import os.path

import numpy as np

from armarx.parser import ArmarXArgumentParser as ArgumentParser
from armarx.ice_manager import is_alive

from visionx.pointclouds import store_point_cloud
from visionx.pointcloud_receiver import PointCloudReceiver

logger = logging.getLogger(__name__)


class PointCloudRecorder:
    def __init__(
        self,
        output_directory: str,
        source_provider_name: str,
        name="PointCloudRecorder",
        max_fps=30,
    ):
        self.output_directory = output_directory
        self.source_provider_name = source_provider_name
        self.name = name
        self.max_fps = max_fps

        # Init receiver.
        self.receiver = PointCloudReceiver(
            name=name, source_provider_name=source_provider_name, wait_for_provider=True
        )
        logger.info(
            f"Wait for point cloud provider '{self.receiver.source_provider_name}' ..."
        )
        self.receiver.on_connect()

        # Prepare replay.
        self.t_start = datetime.datetime.now()
        self.t_latest = None
        self.count = 0

        # Prepare output dir.
        self.directory = os.path.join(output_directory, str(self.t_start))
        logger.info(f"Storing point clouds in '{os.path.abspath(self.directory)}'.")
        os.makedirs(self.directory, exist_ok=True)

    def disconnect(self):
        self.receiver.on_disconnect()

    def record_once(self):
        pc, info = self.receiver.wait_for_next_point_cloud()
        now = datetime.datetime.now()

        if self.t_latest is not None and (now - self.t_latest).total_seconds() < (
            1 / self.max_fps
        ):
            return
        else:
            self.t_latest = now

        # The point cloud we get is read-only, so we need to copy before modifying.
        new_pc: np.ndarray = np.copy(pc)

        filename = f"pointcloud_{now - self.t_start}.npy"
        filepath = os.path.join(self.directory, filename)

        store_point_cloud(filepath, new_pc)
        self.count += 1

        print_step = 10 ** max(1, int(np.log10(self.count)))
        if self.count % print_step == 0:
            logger.info(
                f"Stored {self.count} point clouds (reporting each {print_step}) ..."
            )


def main():

    parser = ArgumentParser()
    parser.add_argument(
        "-o",
        "--output_dir",
        default=".",
        help="The (base) output directory. A sub-directory with a timestamp will be created inside.",
    )
    parser.add_argument(
        "-p",
        "--provider_name",
        default="OpenNIPointCloudProvider",
        help="Name of the input point cloud provider "
        "(e.g. 'OpenNIPointCloudProvider', 'DynamicSimulationDepthImageProvider').",
    )
    parser.add_argument(
        "-n",
        "--name",
        default="PointCloudRecorder",
        help="Name of the created ice object.",
    )

    args = parser.parse_args()

    recorder = PointCloudRecorder(
        output_directory=os.path.expandvars(args.output_dir),
        source_provider_name=args.provider_name,
        name=args.name,
    )

    try:
        while is_alive():
            recorder.record_once()

    except KeyboardInterrupt:
        logger.info("Shutting down.")

    finally:
        recorder.disconnect()


if __name__ == "__main__":
    main()
