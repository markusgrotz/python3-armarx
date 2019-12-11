#!/usr/bin/env python3

from armarx.parser import ArmarXArgumentParser as ArgumentParser
from armarx.ice_manager import is_alive
from armarx.ice_manager import register_object

from armarx.slice_loader import load_armarx_slice
load_armarx_slice('ComponentsExample', 'RNGComponentProviderIceInterface.ice')
from armarx import RNGProviderComponentInterface

import time
import logging
import random


logger = logging.getLogger(__name__)

class RNGProviderComponent(RNGProviderComponentInterface):

    def __init__(self):
        super(RNGProviderComponentInterface, self).__init__()

    def generateRandomInt(self, current=None):
        r = int(random.random() * 10000.0)
        logger.info('returning random variable {}'.format(r))
        return r


def main():
    parser = ArgumentParser(description='RNGProviderComponent')
    parser.parse_args()

    register_object(RNGProviderComponent(), 'RNGProviderComponent')

    try:
        while is_alive():
            logger.debug('Press any key to exit.')
            time.sleep(1.0)
    except KeyboardInterrupt:
        logger.info('shutting down')


if __name__ == '__main__':
    main()
