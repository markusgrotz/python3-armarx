import os
from pathlib import Path
from armarx_core.cmake_helper import get_data_path


def get_package_evn_variable(package_name: str) -> str:
    return dict(
        armarxcore="ArmarXCore_DIR",
        simox="Simox_DIR",
        robotapi="RobotAPI_DIR",
        armarx_control="armarx_control_DIR"
    )[package_name.lower()]


def get_dep_package_dir(package_name: str) -> str:
    return dict(
        eigen="/usr/include/eigen3"
    )[package_name.lower()]


def get_armarx_package_dir(package_name: str) -> Path:
    return Path(os.environ.get(get_package_evn_variable(package_name))).parent


def get_armarx_package_data_dir(package_name: str) -> Path:
    root = get_armarx_package_dir(package_name)
    return root / "data" / package_name


def get_cmake_package_dir(package_name: str) -> Path:
    return Path(get_data_path(package_name)[0]).parent


def get_cmake_package_data_dir(package_name: str) -> Path:
    return Path(get_data_path(package_name)[0]) / package_name
