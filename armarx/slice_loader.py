import logging
import configparser
from importlib.abc import MetaPathFinder

import os
from lxml import etree
from collections import namedtuple

from .interface_helper import load_armarx_slice
from .cmake_helper import get_data_path

import importlib
import types
from .ice_manager import get_proxy
from .ice_manager import get_topic

logger = logging.getLogger(__name__)


VariantInfo = namedtuple('VariantInfo', ['package_name', 'type_name',
                                         'include_path', 'default_name'])


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
                default_name = nav.get('propertyDefaultValue')
                mapping[type_name] = VariantInfo(package_name, type_name, include_path, default_name)
        return mapping

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith('armarx.'):
            return None
        type_name = fullname.split('.')[1]
        variant_info = self.mapping.get(type_name, None)
        if variant_info:
            load_armarx_slice(variant_info.package_name, variant_info.include_path)
            self.patch_slice_definition(variant_info)
        return None

    def patch_slice_definition(self, variant_info):
        default_name = variant_info.default_name

        def get_default_topic(cls, name=None):
            return get_topic(cls, name or default_name)

        def get_default_proxy(cls, name=None):
            return get_proxy(cls, name or default_name)

        mod = importlib.import_module('armarx')
        cls = getattr(mod, variant_info.type_name)
        cls.get_proxy = types.MethodType(get_default_proxy, cls)
        cls.get_topic = types.MethodType(get_default_topic, cls)
