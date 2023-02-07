"""
.. deprecated:: 0.23.4
    module has been moved to .. py:module::`armarx_core.ice_conversion.ice_converter` module
"""

import warnings

warnings.warn(
    "Use 'armarx_core.ice_conversion.ice_converter' instead.", DeprecationWarning
)

from armarx_core.ice_conversion.ice_converter import IceConverter
