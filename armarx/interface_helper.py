import logging

import os
import Ice

from .cmake_helper import get_dependencies, get_include_path

logger = logging.getLogger(__name__)


def load_armarx_slice(project, filename):
    """
    Simple helper function to load a slice definition file.  Definitions in the imported slice
    file are then available through the python import function.

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
