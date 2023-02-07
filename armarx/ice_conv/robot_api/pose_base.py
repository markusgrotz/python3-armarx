"""
.. deprecated:: 0.23.4
    module has been moved to .. py:module::`armarx_core.ice_conversion.robot_api.pose_base` module
"""

import warnings

warnings.warn(
    "Use 'armarx_core.ice_conversion.robot_api.pose_base' instead.", DeprecationWarning
)

from armarx_core.ice_conversion.robot_api.pose_base import Vector3BaseConv, QuaternionBaseConv, PoseBaseConv
