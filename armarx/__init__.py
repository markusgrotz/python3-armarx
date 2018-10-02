import sys
from .proxy_loader import ArmarXVariantInfoFinder

sys.meta_path.insert(0, ArmarXVariantInfoFinder())
