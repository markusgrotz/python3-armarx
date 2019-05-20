#!/usr/bin/env python3

from armarx.parser import ArmarXArgumentParser as ArgumentParser
import time
import logging
import numpy as np

from armarx.data_types import ColoredPoint3D, Point3D, RGBA
from armarx.ice_manager import is_alive
from armarx.pointcloud_provider import PointCloudProvider

logger = logging.getLogger(__name__)


def main():
    parser = ArgumentParser(description='Example Image Provider')
    parser.parse_args()

    result_pc_provider = PointCloudProvider('ExamplePointCloudProvider', 128, 72)
    result_pc_provider.register()

    try:
        while is_alive():
            # TODO: Array creation is awkward
            xyz = np.zeros(128 * 72, dtype=Point3D)
            xyz["x"] = 500 * np.random.rand(128 * 72)
            xyz["y"] = 500 * np.random.rand(128 * 72)
            xyz["z"] = 500 * np.random.rand(128 * 72)
            # xyz = np.array(500*np.random.rand(128*72), dtype=Point3D)
            rgba = np.array(255*np.ones((128*72)), dtype=RGBA)
            pc = np.zeros(128*72, dtype=ColoredPoint3D)
            pc["color"] = rgba
            pc["point"] = xyz
            result_pc_provider.update_pointcloud(pc)
            time.sleep(0.1)
    except KeyboardInterrupt:
        result_pc_provider.shutdown()
        logger.info('shutting down')


if __name__ == '__main__':
    main()
