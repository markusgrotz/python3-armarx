"""
This module automatically injects available slice definitions into the armarx namespace
"""

import sys

from armarx_core.config import CodeGenerationType
from armarx_core.config import get_code_generation_type
from armarx_core.config import get_python_build_dir

from armarx_core.slice_loader import ArmarXProxyFinder


def inject() -> bool:
    """
    :returns: true if the slice loading is activated, false if it was already
    activated
    """
    if get_code_generation_type() == CodeGenerationType.STATIC:
        python_build_dir = get_python_build_dir()
        if python_build_dir in sys.path:
            return False
        sys.path.append(python_build_dir)
        return True
    else:
        if any(isinstance(c, ArmarXProxyFinder) for c in sys.meta_path):
            return False
        sys.meta_path.insert(0, ArmarXProxyFinder())
        return True


# auto inject
inject()
