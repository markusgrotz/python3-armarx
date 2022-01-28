import glob
import logging
import time
import os.path
import re

import numpy as np

from datetime import datetime
from typing import List, Optional

from armarx.ice_manager import is_alive
from visionx.pointcloud_provider import PointCloudProvider
from visionx.pointcloud_provider import dtype_point_color_xyz

logger = logging.getLogger(__name__)


class PointCloudReplayer:

    def __init__(
            self,
            input_directory: str,
            name="PointCloudReplayer",
            loop_back=False,
            default_fps=30,
    ):
        self.input_directory = input_directory
        self.name = name

        self.loop_back = loop_back
        self.default_fps = default_fps

        self.time_format = "%H:%M:%S.%f"
        self.time_regex = re.compile(r"\d*:\d*:\d*.\d*")

        self.t_start = datetime.now()
        self.t_latest = None

        # Find files and load first point cloud.
        self.files: List[str] = []
        self.i = 0
        self.pc: np.ndarray = None

        self._init_files()

        # Initialize provider.
        self.pc_provider: Optional[PointCloudProvider] = None
        self._init_provider()

    def _init_files(self):
        self.files = sorted(glob.glob(os.path.join(self.input_directory, "*.npy")))
        print(f"Found {len(self.files)} files.")

        self.i = 0
        self.pc: np.ndarray = np.load(self.files[self.i])
        print(f"Got shape {self.pc.shape}, dtype {self.pc.dtype}, first point: {self.pc[0]}")

    def _init_provider(self):
        self.pc_provider = PointCloudProvider(
            name=self.name, point_dtype=dtype_point_color_xyz, initial_capacity=len(self.pc))
        self.pc_provider.on_connect()

    def play_once(self) -> bool:
        # Publish the current point cloud.
        self.pc_provider.update_point_cloud(self.pc)
        now = datetime.now()

        # Prepare the next point cloud.
        if self.i == len(self.files) and not self.loop_back:
            print(f"Finished replay.")
            return False

        self.i = (self.i + 1) % len(self.files)
        if self.i == 0:
            print(f"Loop back replay after {len(self.files)} point clouds.")
            self.t_start = now

        # Load next point cloud.
        self.pc = np.load(self.files[self.i])

        # Timing: Wait for next time point.

        # e.g. "pointcloud_0:00:00.311855.npy"
        filename = os.path.splitext(os.path.basename(self.files[self.i]))[0]
        m = self.time_regex.search(filename)
        if m is None:
            # Failed to parse time. Use default FPS.
            if self.t_latest is None:
                due_seconds = 0
            else:
                due_seconds = 1 / self.default_fps - (now - self.t_latest).total_seconds()

        else:
            # Extract target time (relative to start).
            time_str = filename[m.start(): m.end()]
            target_time = datetime.strptime(time_str, self.time_format)

            target_delta = target_time - datetime(year=1900, month=1, day=1)
            passed_delta = now - self.t_start
            due_seconds = target_delta.total_seconds() - passed_delta.total_seconds()

        if due_seconds > 0:
            time.sleep(due_seconds)
        self.t_latest = datetime.now()

        return True


def main():

    replayer = PointCloudReplayer(
        input_directory=os.path.expandvars("$HOME/recorded-point-clouds/2022-01-27 18:57:33.987930"),
    )

    print(f"Start replay of {len(replayer.files)} point clouds ...")
    try:
        while is_alive():
            if not replayer.play_once():
                break

    except KeyboardInterrupt:
        logger.info("Shutting down.")


if __name__ == "__main__":
    main()
