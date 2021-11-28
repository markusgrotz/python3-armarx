import os
import configparser


def _load_config():
    """
    :raises FileNotFoundError: if armarx.ini does not exists
    :returns: the default armarx config
    :rtype: configparser.ConfigParser
    """
    config_file = os.path.join(_get_config_dir(), 'armarx.ini')
    if not os.path.exists(config_file):
        raise FileNotFoundError('ArmarX config file does not exists.')
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def _get_config_dir():

    if os.getenv("ARMARX_USER_CONFIG_DIR"):
        config_dir = os.path.expanduser(os.getenv("ARMARX_USER_CONFIG_DIR"))
        config_dir = os.path.expandvars(config_dir)
    else:
        config_dir = os.path.expanduser('~/.armarx/')

    if not os.path.isdir(config_dir):
        raise FileNotFoundError('ArmarX config folder does not exists.')
    return config_dir


def get_packages():
    """
    Lists all packages that are considered by the statecharts
    """
    default_packages = 'ArmarXGui,RobotAPI,VisionX,RobotSkillTemplates,ArmarXSimulation'
    return config.get('AutoCompletion', 'packages', fallback=default_packages)

def get_ice_config_files():
    """
    The default Ice.Config
    """

    if os.getenv("ARMARX_USER_CONFIG_DIR"):
        config_dir = os.path.expanduser(os.getenv("ARMARX_USER_CONFIG_DIR"))
        config_dir = os.path.expandvars(config_dir)
    else:
        config_dir = os.path.expanduser('~/.armarx/')


#     config_dir = os.path.expanduser('~/.armarx/')
    return [os.path.join(config_dir, 'default.generated.cfg'),
            os.path.join(config_dir, 'default.cfg')]


config = _load_config()
