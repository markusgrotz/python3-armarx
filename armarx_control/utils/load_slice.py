import sys
from typing import Any
from armarx_core import ice_manager
from armarx_core.slice_loader import ArmarXProxyFinder
from robot_utils import console


def load_slice(armarx_package_name: str, filename: str):
    for c in sys.meta_path:
        if isinstance(c, ArmarXProxyFinder):
            c._load_slice_file(armarx_package_name, filename)
            c.update_loaded_modules()


def load_proxy(proxy_name: str, proxy_type: Any):
    console.rule(f"[bold blue]Configuring {proxy_name}")
    ice_manager.wait_for_proxy(proxy_type, proxy_name)
    component = ice_manager.get_proxy(proxy_type, proxy_name)
    console.log(f"{proxy_name} connected")
    return component
