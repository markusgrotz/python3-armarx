#!/usr/bin/env python3

from armarx.parser import ArmarXArgumentParser as ArgumentParser
import time
import logging
import numpy as np

from armarx.ice_manager import is_alive
from armarx.image_provider import ImageProvider

logger = logging.getLogger(__name__)


def main():
    parser = ArgumentParser(description='Example Image Provider')
    parser.parse_args()

    result_image_provider = ImageProvider('ExampleImageProvider', 1, 128, 72)
    result_image_provider.register()

    try:
        while is_alive():
            im = np.random.random(result_image_provider.data_dimensions) * 255.0
            result_image_provider.update_image(im)
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info('shutting down')


if __name__ == '__main__':
    main()
