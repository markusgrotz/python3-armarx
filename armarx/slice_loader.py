"""
.. deprecated:: 0.20.1
    module is moved to .. py:module::`armarx_core.slice_loader` package
"""
import sys
import warnings

from armarx_core.slice_loader import ArmarXProxyFinder


def load_armarx_slice(armarx_package_name: str, filename: str):
    """
    .. deprecated:: 0.10.6

        add your slice file to a project's VariantInfo-*.xml instead
    """
    warnings.warn(
        "Add the slice definition to VariantInfo-*.xml instead.", DeprecationWarning
    )
    for c in sys.meta_path:
        if isinstance(c, ArmarXProxyFinder):
            c._load_armarx_slice(armarx_package_name, filename)
            c.update_loaded_modules()
