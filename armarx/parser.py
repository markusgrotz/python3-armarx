from argparse import ArgumentParser

import sys
import logging

from .ice_manager import test_connection


class ArmarXArgumentParser(ArgumentParser):
    """
    ArgumentParser with default arguments

    ..see:: argparse.ArgumentParser

    ..highlight:: python
    ..codeblock:: python

        from armarx.parser import ArmarXArgumentParser as ArgumentParser

        parser = ArgumentParser('test')
        parser.add_argument(...)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse_args(self):
        self.add_argument(
            "--skip-connection-test",
            action="store_true",
            help="Do not test the connection",
        )
        verbose_group = self.add_mutually_exclusive_group()
        verbose_group.add_argument(
            "-v", "--verbose", action="store_true", help="be verbose"
        )
        verbose_group.add_argument(
            "-q", "--quiet", action="store_true", help="be quiet"
        )

        args = super().parse_args()

        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        if args.verbose:
            logging.basicConfig(
                format=log_format, stream=sys.stdout, level=logging.DEBUG
            )
        elif args.quiet:
            logging.basicConfig(
                format=log_format, stream=sys.stdout, level=logging.ERROR
            )
        else:
            logging.basicConfig(
                format=log_format, stream=sys.stdout, level=logging.INFO
            )

        if not args.skip_connection_test:
            test_connection()

        return args
