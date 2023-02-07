"""
.. deprecated:: 0.23.4
    module has been moved to .. py:module::`armarx_core.tool.metronome` module
"""

import warnings

warnings.warn(
    "Use armarx_core.tools.metronome instead.", DeprecationWarning
)

from armarx_core.tools.metronome import Metronome
