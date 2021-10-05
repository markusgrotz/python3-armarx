"""
This module automatically injects available slice definitions into the armarx namespace
"""

import sys

from .slice_loader import ArmarXProxyFinder

sys.meta_path.insert(0, ArmarXProxyFinder())
