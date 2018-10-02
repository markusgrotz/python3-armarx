from .ice_manager import test_connection

import sys
from .proxy_loader import ArmarXVariantInfoFinder

test_connection()

sys.meta_path.insert(0, ArmarXVariantInfoFinder())
