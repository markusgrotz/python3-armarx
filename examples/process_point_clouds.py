import logging
import time
import math

from armarx.ice_manager import is_alive
from armarx.point_clouds import PointCloudProcessor

logger = logging.getLogger(__name__)


def main():
    pp = PointCloudProcessor("ExamplePointCloudProcessor",
                             source_provider_name="OpenNIPointCloudProvider")

    pp.on_connect()

    try:
        while is_alive():
            pc, info = pp.wait_for_next_point_cloud()
            print("PC:", pc.shape)
            # pass

            # TODO: Modify pc and publish via result provider

    except KeyboardInterrupt:
        logger.info('shutting down')


if __name__ == '__main__':
    main()