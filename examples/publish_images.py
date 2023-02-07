#!/usr/bin/env python3

import time
import logging
import numpy as np

from armarx_vision.image_provider import ImageProvider

from armarx_core.ice_manager import is_alive
from armarx_core.parser import ArmarXArgumentParser as ArgumentParser

logger = logging.getLogger(__name__)


def main():
    parser = ArgumentParser(description="Example Image Provider")
    parser.add_argument("-d", "--delay", default=0.1, type=float)
    args = parser.parse_args()

    result_image_provider = ImageProvider("ExampleImageProvider", 2, 640, 480)
    result_image_provider.register()

    try:
        while is_alive():
            random_images = np.random.randint(
                0, 255, result_image_provider.data_dimensions, dtype=np.uint8
            )
            time_provided = int(time.time() * 1000.0 * 1000.0)
            time.sleep(args.delay)
            result_image_provider.update_images(random_images, time_provided)
    except KeyboardInterrupt:
        logger.info("shutting down")


if __name__ == "__main__":
    main()
