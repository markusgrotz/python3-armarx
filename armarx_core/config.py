import os
import configparser

from enum import Enum
from typing import List

import logging


logger = logging.getLogger(__name__)


def _load_config() -> configparser.ConfigParser:
    """
    :raises FileNotFoundError: if armarx.ini does not exists
    :returns: the default armarx config
    :rtype: configparser.ConfigParser
    """
    config_file = os.path.join(_get_config_dir(), "armarx.ini")
    if not os.path.exists(config_file):
        raise FileNotFoundError("ArmarX config file does not exists.")
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return config_parser


def _get_config_dir():
    """
    Returns the current armarx config directory. Therefore this methods first
    checks if the configuration is given by an environment variable, or a
    workspace is currently loaded. Otherwise it tests the default path

    :returns: the current config directory
    """
    if os.environ.get("ARMARX_USER_CONFIG_DIR", None):
        config_dir = os.path.expanduser(os.environ["ARMARX_USER_CONFIG_DIR"])
    elif os.environ.get("ARMARX_WORKSPACE", None):
        config_dir = os.path.join(os.environ["ARMARX_WORKSPACE"], "armarx_config")
    else:
        config_dir = os.path.expanduser("~/.armarx/")

    if config_dir:
        config_dir = os.path.expandvars(config_dir)
    if os.path.isdir(config_dir):
        return config_dir
    else:
        raise FileNotFoundError(
            f'ArmarX config folder does not exists. (Tried: "{config_dir}")'
        )


def get_packages() -> str:
    """
    Lists all packages that are considered by the statecharts
    """
    default_packages = (
        "ArmarXCore,ArmarXGui,RobotAPI,VisionX,RobotSkillTemplates,ActiveVision"
    )
    return config.get("AutoCompletion", "packages", fallback=default_packages)


def get_ice_config_files() -> List[str]:
    """
    The default Ice.Config
    """
    config_dir = _get_config_dir()
    return [
        os.path.join(config_dir, "default.generated.cfg"),
        os.path.join(config_dir, "default.cfg"),
    ]


def get_python_build_dir() -> str:
    if os.environ.get("ARMARX_PYTHON_BUILD_DIR", None):
        return os.path.expandvars(os.environ["ARMARX_PYTHON_BUILD_DIR"])


class CodeGenerationType(Enum):
    DYNAMIC = 0
    STATIC = 1


def get_code_generation_type():
    if config.get("Misc", "PythonStaticCode", fallback=None):
        python_binary_dir = get_python_build_dir()
        if os.path.exists(python_binary_dir):
            return CodeGenerationType.STATIC
        else:
            logger.warning(
                "Static python code selected but directory %s does not exists",
                python_binary_dir,
            )
    return CodeGenerationType.DYNAMIC


config = _load_config()
