#!/usr/bin/env python3

from armarx.parser import ArmarXArgumentParser as ArgumentParser
from armarx import ice_manager
from armarx import slice_loader 

slice_loader.load_armarx_slice('ComponentsExample', 'RNGComponentProviderIceInterface.ice')
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

    ice_manager.register_object(RNGProviderComponent(), 'RNGProviderComponent')
    ice_manager.wait_for_shutdown()

if __name__ == '__main__':
    main()
