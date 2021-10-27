"""
Module containing all the logic to handle and import slice files
"""

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


ArmarXProxyInfo = namedtuple('ArmarXProxyInfo', ['package_name', 'fullname',
                                                 'include_path', 'default_name'])

def load_armarx_slice(armarx_package_name: str, filename: str):
    """
    ..deprecated:: add your slice file to a project's VariantInfo-*.xml instead
    """
    warnings.warn('Add the slice definition to VariantInfo-*.xml instead.', DeprecationWarning)
    _load_armarx_slice(armarx_package_name, filename)

def _load_armarx_slice(armarx_package_name: str, filename: str):
    """
    Simple helper function to load a slice definition file.

    Loads a slice definition file from a project. Definitions in the imported
    slice file are then available through the python import function.

    :raises IOError: if the slice file was not found
    :param armarx_package_name: name of the armarx package
    :param filename: relative path to the slice interface
    """
    package_dependencies = get_dependencies(armarx_package_name)
    package_dependencies.append(armarx_package_name)
    if "ArmarXCore" not in package_dependencies:
        package_dependencies = ["ArmarXCore"] + package_dependencies

    include_paths = ['-I{}'.format(Ice.getSliceDir())]

    for package_name in package_dependencies:
        interface_include_path = get_include_path(package_name)
        include_paths.extend(interface_include_path)

    filename = os.path.join(include_paths[-1], armarx_package_name, 'interface', filename)
    filename = os.path.abspath(filename)

    search_path = ' -I'.join(include_paths)
    logger.debug('Looking for slice files in %s', search_path)
    if not os.path.exists(filename):
        raise IOError("Path not found: " + filename)
    Ice.loadSlice('{} --underscore --all {}'.format(search_path, filename))



class ArmarXProxyFinder(MetaPathFinder):
    """
    The ArmarXProxyFinder class

    Searches all known proxy/topic definitions as specified by
    config.get_packages() and adds them as available module to Python

    ..see:: config.get_package
    ..see:: importlib.abc.MetaPathFinder
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # all namespaces as specified by the slice definitions
        self.package_namespaces = {'armarx', 'visionx'}
        # all patched interfaces
        self.patched_definitions = set()
        # mapping between fullname of the proxies/topics and variant info
        self.mapping = self._build_mapping()

    def _build_mapping(self):
        global_mapping = dict()
        armarx_packages = get_packages()
        for package_name in armarx_packages.split(','):
            global_mapping.update(self._load_variant_info(package_name))
        return global_mapping


    def _load_variant_info(self, armarx_package_name: str):
        mapping = dict()
        data_path = get_data_path(armarx_package_name)
        if not data_path:
            logger.warning('unable to get data path for package %s', armarx_package_name)
            return mapping
        variant_path = os.path.join(data_path[0], armarx_package_name,
                                    'VariantInfo-{}.xml'.format(armarx_package_name))
        if not os.path.isfile(variant_path):
            logger.warning('variant info does not exists for package %s', armarx_package_name)
            return mapping
        tree = etree.parse(variant_path)
        start_pos = len(armarx_package_name + '/interface/')
        for definition_type in ['Proxy', 'Topic']:
            for nav in tree.xpath('//VariantInfo/Lib/' + definition_type):
                fullname = nav.get('typeName').replace('::', '.')
                if not '.' in fullname:
                    fullname = f'armarx.{fullname}'
                python_package_name, _type_name = fullname.rsplit('.', 1)
                self.package_namespaces.add(python_package_name)
                # ..todo add sanity check. remove .h and and .ice
                slice_include_path = nav.get('include')[start_pos:-2] + '.ice'
                proxy_default_name = nav.get('propertyDefaultValue')
                mapping[fullname] = ArmarXProxyInfo(armarx_package_name, fullname,
                                                    slice_include_path, proxy_default_name)
                if fullname.endswith('Prx'):
                    fullname = fullname[:-3]
                    mapping[fullname] = ArmarXProxyInfo(armarx_package_name, fullname,
                                                        slice_include_path, proxy_default_name)
        return mapping

    def find_spec(self, fullname, path, target=None):
        """
        ..see:: importlib.abc.MetaPathFinder.find_spec
        """
        if not fullname in self.mapping:
            return None

        variant_info = self.mapping.get(fullname)
        load_armarx_slice(variant_info.package_name, variant_info.include_path)
        self.patch_slice_definition(variant_info)

        for _, variant_info in self.mapping.items():
            if variant_info.fullname in sys.modules:
                if variant_info.fullname in self.patched_definitions:
                    continue
                else:
                    self.patch_slice_definition(variant_info)
        return None

    def patch_slice_definition(self, variant_info):
        """
        Adds get_proxy, get_topic, and other methods to the imported interface
        """
        default_name = variant_info.default_name


        # already patched. No need to do it again.
        if variant_info.fullname in self.patched_definitions:
            return

        package_name, type_name = variant_info.fullname.rsplit('.', 1)

        mod = importlib.import_module(package_name)


        if not hasattr(mod, type_name):
            return

        cls = getattr(mod, type_name)

        def _get_default_topic(cls, name=None):
            return get_topic(cls, name or default_name)

        def _get_default_proxy(cls, name=None):
            return get_proxy(cls, name or default_name)

        def _wait_for_default_proxy(cls, name=None, timeout=0):
            return wait_for_proxy(cls, name or default_name, timeout)

        if type_name.endswith('Prx'):
            proxy_class = cls
        else:
            proxy_class = getattr(mod, type_name + 'Prx')

        cls.get_topic = types.MethodType(_get_default_topic, proxy_class)
        cls.get_proxy = types.MethodType(_get_default_proxy, proxy_class)
        cls.wait_for_proxy = types.MethodType(_wait_for_default_proxy, proxy_class)

        self.patched_definitions.add(variant_info.fullname)
