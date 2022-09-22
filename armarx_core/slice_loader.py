"""
Module containing all the logic to handle and import slice files
"""
import os
import sys
import logging
import time

import warnings

import inspect

from importlib.abc import MetaPathFinder
import importlib
import types

import Ice


from .ice_manager import get_proxy
from .ice_manager import get_topic
from .ice_manager import register_object
from .ice_manager import wait_for_proxy

from .cmake_helper import get_include_path
from .cmake_helper import get_dependencies

from .name_helper import slice_mapping

logger = logging.getLogger(__name__)


def load_armarx_slice(armarx_package_name: str, filename: str):
    """
    ..deprecated:: add your slice file to a project's VariantInfo-*.xml instead
    """
    warnings.warn(
        "Add the slice definition to VariantInfo-*.xml instead.", DeprecationWarning
    )
    for c in sys.meta_path:
        if isinstance(c, ArmarXProxyFinder):
            c._load_armarx_slice(armarx_package_name, filename)
            c.update_loaded_modules()

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
        self.package_namespaces = {"armarx", "visionx"}
        # all patched interfaces
        self.patched_definitions = set()
        self.loaded_slice_files = set()
        # mapping between fullname of the proxies/topics and variant info
        self.mapping = slice_mapping
        for _, v in self.mapping.items():
            python_package_name, _type_name = v.fullname.rsplit(".", 1)
            self.package_namespaces.add(python_package_name)


    def _load_armarx_slice(self, armarx_package_name: str, filename: str):
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

        include_paths = ["-I{}".format(Ice.getSliceDir())]

        for package_name in package_dependencies:
            interface_include_path = get_include_path(package_name)
            if interface_include_path:
                include_paths.extend(interface_include_path)
            else:
                logger.error("Include path for project %s is empty", package_name)
                raise Exception(f"Invalid include path for project {package_name}")

        filename = os.path.join(
            include_paths[-1], armarx_package_name, "interface", filename
        )
        filename = os.path.abspath(filename)

        search_path = " -I".join(include_paths)
        logger.debug("Looking for slice files in %s", search_path)
        if not os.path.exists(filename):
            raise IOError("Path not found: " + filename)
        Ice.loadSlice("{} --underscore --all {}".format(search_path, filename))


    def update_loaded_modules(self):
        """
        Update
        """
        for _, variant_info in self.mapping.items():

            if variant_info.fullname in self.patched_definitions:
                continue

            module_name, x = variant_info.fullname.rsplit('.', maxsplit=1)

            if module_name in sys.modules:
                module = sys.modules[module_name]
                if hasattr(module, x):
                    self.patch_slice_definition(variant_info)


    def find_spec(self, fullname, path, target=None):
        """
        ..see:: importlib.abc.MetaPathFinder.find_spec
        """
        if not fullname in self.mapping:
            return None

        variant_info = self.mapping.get(fullname)

        loaded_slice = f"{variant_info.package_name}/{variant_info.include_path}"
        if loaded_slice in self.loaded_slice_files:
            self.update_loaded_modules()
            return None

        self._load_armarx_slice(variant_info.package_name, variant_info.include_path)

        self.loaded_slice_files.add(loaded_slice)

        if variant_info.type == "Class":
            return None

        self.patch_slice_definition(variant_info)

        self.update_loaded_modules()

        return None

    def patch_slice_definition(self, variant_info):
        """
        Adds get_proxy, get_topic, and other methods to the imported interface
        """
        default_name = variant_info.default_name

        # already patched. No need to do it again.
        if variant_info.fullname in self.patched_definitions:
            return

        package_name, type_name = variant_info.fullname.rsplit(".", 1)

        mod = importlib.import_module(package_name)

        if not hasattr(mod, type_name):
            return

        cls = getattr(mod, type_name)

        def _get_default_topic(cls, name=None):
            return get_topic(cls, name)

        def _get_default_proxy(cls, name=None):
            return get_proxy(cls, name)

        def _wait_for_default_proxy(cls, name=None, timeout=0):
            return wait_for_proxy(cls, name, timeout)

        def _register_object(self, name: str):
            return register_object(self, name)

        if type_name.endswith("Prx"):
            proxy_class = cls
        elif hasattr(mod, type_name + "Prx"):
            proxy_class = getattr(mod, type_name + "Prx")
        else:
            return

        cls.get_topic = types.MethodType(_get_default_topic, proxy_class)
        cls.get_proxy = types.MethodType(_get_default_proxy, proxy_class)
        cls.wait_for_proxy = types.MethodType(_wait_for_default_proxy, proxy_class)
        cls.default_name = default_name

        self.patched_definitions.add(variant_info.fullname)
