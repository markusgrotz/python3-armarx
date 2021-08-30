import os
import sys
import logging
from collections import namedtuple

import warnings

from importlib.abc import MetaPathFinder
import importlib
import types

from lxml import etree

import Ice

from .cmake_helper import get_data_path

from .ice_manager import get_proxy
from .ice_manager import get_topic
from .ice_manager import wait_for_proxy

from .cmake_helper import get_dependencies, get_include_path

from .config import get_packages

logger = logging.getLogger(__name__)


VariantInfo = namedtuple('VariantInfo', ['package_name', 'type_name',
                                         'include_path', 'default_name'])


def load_armarx_slice(project, filename):
    """
    Simple helper function to load a slice definition file.
    
    
    Loads a slice definition file from a project. Definitions in the imported
    slice file are then available through the python import function.

    :raises IOError: if the slice file was not found
    :param project: name of the armarx package
    :type project: str
    :param filename: relative path to the slice interface
    :type filename: str
    """
    dependencies = get_dependencies(project)
    dependencies.append(project)

    include_path = ['-I{}'.format(Ice.getSliceDir())]

    for package_name in dependencies:
        interface_dir = get_include_path(package_name)
        include_path.extend(interface_dir)

    filename = os.path.join(include_path[-1], project, 'interface', filename)

    search_path = ' -I'.join(include_path)
    logger.debug('Looking for slice files in {}'.format(search_path))
    if not os.path.exists(filename):
        raise IOError("Path not found: " + filename)
    Ice.loadSlice('{} --underscore --all {}'.format(search_path, filename))


class ArmarXVariantInfoFinder(MetaPathFinder):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mapping = self.build_mapping()
        self.patched = {}

    def build_mapping(self):
        global_mapping = dict()
        packages = get_packages()
        for package_name in packages.split(','):
            global_mapping.update(self.load_variant_info(package_name))
        return global_mapping

    def load_variant_info(self, package_name):
        mapping = dict()
        data_path = get_data_path(package_name)
        if not data_path:
            logger.warn('unable to get data path for package {}'.format(package_name))
            return
        variant_path = os.path.join(data_path[0], package_name, 'VariantInfo-{}.xml'.format(package_name))
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
            # ..todo:: we need to patch all interfaces since an interface might
            # be already loaded
            for _, variant_info in self.mapping.items():
                self.patch_slice_definition(variant_info)
        else:
            print(f"Variant info {fullname} could not be loaded")
        return None

    def patch_slice_definition(self, variant_info: VariantInfo):
        """
        Adds get_proxy, get_topic, and other methods to the imported interface
        """
        default_name = variant_info.default_name

        if variant_info.type_name in self.patched:
            return

        def patch_module(mod: str):

            try:
                print(f"Patching module {mod}")
                if not hasattr(mod, variant_info.type_name):
                    return

                cls = getattr(mod, variant_info.type_name)

                def _get_default_topic(cls, name=None):
                    return get_topic(cls, name or default_name)

                def _get_default_proxy(cls, name=None):
                    return get_proxy(cls, name or default_name)

                def _wait_for_default_proxy(cls, name=None, timeout=0):
                    return wait_for_proxy(cls, name or default_name, timeout)

                cls.get_proxy = types.MethodType(_get_default_proxy, cls)
                cls.get_topic = types.MethodType(_get_default_topic, cls)
                cls.wait_for_proxy = types.MethodType(_wait_for_default_proxy, cls)

                self.patched[variant_info.type_name] = True
            except:
                print(f"Could not patch module '{mod.__str__()}'")

        mod = importlib.import_module('armarx')
        patch_module(mod)

        mod = importlib.import_module(variant_info.package_name)
        patch_module(mod)