import logging
import configparser
from importlib.abc import MetaPathFinder

import os
from lxml import etree

from .interface_helper import load_armarx_slice
from .cmake_helper import get_data_path

import importlib
import types
from .interface_helper import get_proxy
from .interface_helper import get_topic

logger = logging.getLogger(__name__)


class ArmarXVariantInfoFinder(MetaPathFinder):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mapping = self.build_mapping()

    def build_mapping(self):
        global_mapping = dict()
        parser = configparser.ConfigParser()
        parser.read(os.path.expanduser('~/.armarx/armarx.ini'))
        packages = parser.get('AutoCompletion', 'packages')
        for package_name in packages.split(','):
            global_mapping.update(self.load_variant_info(package_name))
        return global_mapping

    def load_variant_info(self, package_name):
        mapping = dict()
        variant_path = os.path.join(get_data_path(package_name)[0], package_name, 'VariantInfo-{}.xml'.format(package_name))
        if not os.path.exists(variant_path):
            logger.warn('unable to read variant info for package {}'.format(package_name))
            return mapping
        tree = etree.parse(variant_path)
        start_pos = len(package_name + '/interface/')
        for t in ['Proxy', 'Topic']:
            for nav in tree.xpath('//VariantInfo/Lib/' + t):
                type_name = nav.get('typeName').split('::')[-1]
                include_path = nav.get('include')[start_pos:-2] + '.ice'
                mapping[type_name] = package_name, include_path
        return mapping

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith('armarx.'):
            return None
        type_name = fullname.split('.')[1]
        package_name, include_path = self.mapping.get(type_name, (None, None))
        if package_name and include_path:
            load_armarx_slice(package_name, include_path)
            self.patch_slice_definition(type_name)
        return None

    def patch_slice_definition(self, type_name):
        mod = importlib.import_module('armarx')
        cls = getattr(mod, type_name)
        cls.get_proxy = types.MethodType(get_proxy, cls)
        cls.get_topic = types.MethodType(get_topic, cls)
