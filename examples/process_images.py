#!/usr/bin/env python3

import logging

from armarx.parser import ArmarXArgumentParser as ArgumentParser
from armarx.image_processor import ImageProcessor

import numpy as np

logger = logging.getLogger(__name__)


class TestImageProcessor(ImageProcessor):

    def process_image(self, images):
        return np.random.random(images.shape)


def main():
    parser = ArgumentParser('Example Image Provider')
    parser.parse_args()

    logger.debug('Starting example image processor')

    image_processor = TestImageProcessor('Armar3ImageProvider')
    image_processor.register()


if __name__ == '__main__':
    main()
