"""
.. deprecated:: 0.23.4
    module has been moved to .. py:module::`armarx_core.ice_conversion.armarx_core.basic_vector_types` module
"""

import warnings

warnings.warn(
    "Use 'armarx_core.ice_conversion.armarx_core.basic_vector_types' instead.", DeprecationWarning
)

from armarx_core.ice_conversion.armarx_core.basic_vector_types import Vector2fConv, Vector3fConv
