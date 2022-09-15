import logging

import os
import subprocess
from functools import lru_cache

from typing import List

logger = logging.getLogger(__name__)


@lru_cache(maxsize=32)
def get_armarx_include_dirs(pkg_name: str) -> List[str]:
    """
    find the include dir path for an armarx package

    :param pkg_name: name of the package
    :returns: the include path to the package if found
    :rtype: str
    """
    cmd = [
        "cmake",
        "--find-package",
        f"-DNAME={pkg_name}",
        "-DCOMPILER_ID=GNU",
        "-DLANGUAGE=C",
        "-DMODE=COMPILE",
    ]
    result = subprocess.check_output(cmd).decode("utf-8")
    includes = []
    path_list = result.split("-I")
    for path in path_list:
        if path.strip():
            includes.append(path.strip())
    return includes


@lru_cache(maxsize=32)
def get_data_path(package_name: str) -> List[str]:
    return get_package_information(package_name, "DATA_DIR:")


def get_dependencies(package_name: str, include_self=False) -> List[str]:
    dependencies = get_package_information(package_name, "SOURCE_PACKAGE_DEPENDENCIES:")
    dependencies = dependencies or []
    # manually add ArmarXCore
    if not "ArmarXCore" in dependencies:
        dependencies.append("ArmarXCore")
    if include_self and is_armarx_package(package_name):
        dependencies.append(package_name)
        return dependencies
    else:
        return dependencies or []


@lru_cache(maxsize=32)
def get_include_path(package_name: str) -> List[str]:
    return get_package_information(package_name, "INTERFACE_DIRS:")


def get_build_path(package_name: str) -> List[str]:
    return get_package_information(package_name, "BUILD_DIR:")


def get_package_information(package_name: str, info) -> List[str]:
    package_data = get_package_data(package_name)
    for l in package_data.split("\n"):
        if info in l:
            if l.endswith(":"):
                return []
            l = l.split(":")[1]
            return l.split(";")


@lru_cache(maxsize=32)
def get_package_data(package_name: str):
    if not package_name:
        logger.error("package name is empty.")
        return
    rel_cmake_script = "ArmarXCore/core/system/cmake/FindPackageX.cmake"
    includes = get_armarx_include_dirs("ArmarXCore")
    for include in includes:
        cmake_script = os.path.join(include, rel_cmake_script)
        if os.path.exists(cmake_script):
            armarx_cmake_script = cmake_script
            cmd = [
                "cmake",
                "-DPACKAGE={}".format(package_name),
                "-P",
                armarx_cmake_script,
            ]
            return subprocess.check_output(cmd).decode("utf-8")
    logger.error("Could not find %s for ArmarXCore in %s", rel_cmake_script, includes)
    raise ValueError("Could not find a valid ArmarXCore path!")


def is_armarx_package(package_name: str) -> bool:
    package_data = get_package_data(package_name)
    return package_data.strip()


@lru_cache(maxsize=32)
def find_cmake_package(
    package_name: str,
    package_cache_dir: str = "~/.cmake/packages",
) -> str:
    """
    Find a CMake package using the package cache.

    :param package_name: The name of the CMake project.
    :param package_cache_dir: The directory of the cmake package cache.
    :return: The absolute path to the package root.
    :raise: IOError If the package cannot be found.
    """
    cmake_package_cache_dir = os.path.expanduser(package_cache_dir)
    directory = os.path.join(cmake_package_cache_dir, package_name)

    if not os.path.isdir(directory):
        msg = "Could not find CMake package '{}' in CMake package cache '{}'.".format(
            package_name, cmake_package_cache_dir
        )

        # Case mismatch?
        dirs = sorted(os.listdir(cmake_package_cache_dir))
        dirs_lower = [d.lower() for d in dirs]
        try:
            index = dirs_lower.index(package_name.lower())
            msg += f"\nDid you mean '{dirs[index]}'?"
        except ValueError:
            pass

        raise IOError(msg)

    files = os.listdir(directory)
    if len(files) == 1:
        with open(os.path.join(directory, files[0])) as file:
            content = file.read()
        build_dir = content.strip()
        root_dir, build = os.path.split(build_dir)
        if build != "build":
            raise IOError("Something strange")
        return root_dir

    elif len(files) == 0:
        msg = f"Found no file in directory: {directory}"
        raise IOError(msg)

    else:
        msg = "Found more than one file with the following contents:"
        for filename in sorted(files):
            with open(os.path.join(directory, filename)) as file:
                content = file.read().strip()
            msg += f"\n- {file}: \t{content}"
        raise IOError(msg)
