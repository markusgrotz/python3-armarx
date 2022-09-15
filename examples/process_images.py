#!/usr/bin/env python3

import logging

from armarx.parser import ArmarXArgumentParser as ArgumentParser
from visionx.image_processor import ImageProcessor

import numpy as np

logger = logging.getLogger(__name__)


class TestImageProcessor(ImageProcessor):
    def process_images(self, images, info):
        info.timeProvided = 1633428148974550
        return np.random.random(images.shape) * 128, info


def main():
    parser = ArgumentParser("Example Image Provider")
    parser.parse_args()

    logger.debug("Starting example image processor")

    image_processor = TestImageProcessor("OpenNIPointCloudProvider")
    image_processor.register()


if __name__ == "__main__":
    main()
