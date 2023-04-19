#|\---/|
#| o_o |
# \_^_/
# Im a bit unsire if this is the way to do these redirects. It should probably just be import armarx_core.tools as that actually just calls the proper __init__.py
# If you have errors here check if the __init__.py of armarx_core.tools has changed!

import warnings

warnings.warn(
    "Use 'armarx_core.tools' instead.", DeprecationWarning
)

from armarx_core.tools import metronome
