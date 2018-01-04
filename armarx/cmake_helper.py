import logging

import os
import subprocess

logger = logging.getLogger(__name__)


def get_armarx_pkg_dir(pkg_name):
    """
    finds the package path for an armarx package


    .. fixme: this does not work for installed packages

    :param pkg_name: name of the package
    :returns: the path to the package if found
    :rtype: str
    """
    path = os.path.expanduser('~/.cmake/packages/{}/'.format(pkg_name))
    l = list(os.listdir(path))
    if len(l) != 1:
        logger.error('unable to find path for package {}. path is not unique'.format(pkg_name))
        raise ValueError('unable to find cmake package path')
    with open(os.path.join(path, l[0])) as f:
        lines = f.readlines()
    if len(lines) != 1:
        logger.error('unable to find path for package {}'.format(pkg_name))
        raise ValueError('unable to find cmake package path')
    else:
        for line in open(os.path.join(lines[0][:-1], 'CMakeCache.txt')):
            if line.startswith('Project_SOURCE_DIR'):
                return line.split('=')[-1][:-1]


def get_data_path(package_name):
    return get_package_information(package_name, 'DATA_DIR:')


def get_dependencies(package_name):
    return get_package_information(package_name, 'SOURCE_PACKAGE_DEPENDENCIES:')


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
    cmake_script = os.path.join(get_armarx_pkg_dir('ArmarXCore'), 'source/ArmarXCore/core/system/cmake/FindPackageX.cmake')
    cmd = ['cmake', '-DPACKAGE={}'.format(package_name), '-P', cmake_script]
    return subprocess.check_output(cmd).decode('utf-8')


def is_armarx_package(package_name):
    package_data = get_package_data(package_name)
    return package_data.strip()
