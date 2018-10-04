from argparse import ArgumentParser

import sys
import logging


class ArmarXArgumentParser(ArgumentParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse_args(self):
        verbose_group = self.add_mutually_exclusive_group()
        verbose_group.add_argument('-v', '--verbose', action='store_true', help='be verbose')
        verbose_group.add_argument('-q', '--quiet', action='store_true', help='be quiet')

        args = super().parse_args()

        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        if args.verbose:
            logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.DEBUG)
        elif args.quiet:
            logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.ERROR)
        else:
            logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.INFO)

        return args
