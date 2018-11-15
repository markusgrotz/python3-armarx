import logging

import os
import subprocess

logger = logging.getLogger(__name__)
# make global var since finding it is expensive
armarx_cmake_script = None

def get_armarx_include_dirs(pkg_name):
    """
    finds the package path for an armarx package


    .. fixme: this does not work for installed packages

    :param pkg_name: name of the package
    :returns: the path to the package if found
    :rtype: str
    """

    cmd = ["cmake", "--find-package", "-DNAME=" + pkg_name, "-DCOMPILER_ID=GNU", "-DLANGUAGE=C",  "-DMODE=COMPILE"]
    result = subprocess.check_output(cmd).decode("utf-8")
    includes = []
    path_list = result.split("-I")
    for path in path_list:
        if len(path.strip()) > 0:
            includes.append(path.strip())
    return includes


def get_data_path(package_name):
    return get_package_information(package_name, 'DATA_DIR:')


def get_dependencies(package_name, include_self=False):
    dependencies = get_package_information(package_name, 'SOURCE_PACKAGE_DEPENDENCIES:')
    if include_self and is_armarx_package(package_name):
        dependencies.append(package_name)
        return dependencies
    else:
        return dependencies or []


def get_include_path(package_name):
    return get_package_information(package_name, 'INTERFACE_DIRS:')


def get_package_information(package_name, info):
    package_data = get_package_data(package_name)
    for l in package_data.split('\n'):
        if info in l:
            if l.endswith(':'):
                return []
            l = l.split(':')[1]
            return l.split(';')


def get_package_data(package_name):
    if not package_name:
        logger.error('package name is empty.')
        return
    rel_cmake_script = 'ArmarXCore/core/system/cmake/FindPackageX.cmake'
    includes = get_armarx_include_dirs('ArmarXCore')
    global armarx_cmake_script
    if armarx_cmake_script is None:
        for include in includes:
            cmake_script = os.path.join(include, rel_cmake_script)
            logger.info("Checking " + cmake_script)
            if os.path.exists(cmake_script):
                armarx_cmake_script = cmake_script
                break
    if armarx_cmake_script:
        cmd = ['cmake', '-DPACKAGE={}'.format(package_name), '-P', armarx_cmake_script]
        return subprocess.check_output(cmd).decode('utf-8')
    else:
        logger.error("Could not find " + rel_cmake_script + " for ArmarXCore in " + (", ").join(includes))
        raise ValueError("Could not find a valid ArmarXCore path!")

def is_armarx_package(package_name):
    package_data = get_package_data(package_name)
    return package_data.strip()
