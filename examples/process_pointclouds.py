import logging

from armarx.parser import ArmarXArgumentParser as ArgumentParser
from armarx.pointcloud_processor import PointCloudProcessor

import numpy as np

logger = logging.getLogger(__name__)


class TestPointCloudProcessor(PointCloudProcessor):

    def process_pointcloud(self, pointclouds):
        # print(pointclouds)
        return pointclouds


def main():
    parser = ArgumentParser('Example PointCloud Provider')
    parser.parse_args()

    logger.debug('Starting example image processor')

    image_processor = TestPointCloudProcessor("DynamicSimulationDepthImageProvider")
    image_processor.register()


if __name__ == '__main__':
    main()
