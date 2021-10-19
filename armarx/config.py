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
    if os.environ["ARMARX_WORKSPACE"]:
        config_dir = os.path.join(os.environ['ARMARX_WORKSPACE'], 'armarx_config')
    else:
        config_dir = os.path.expanduser('~/.armarx/')

    if os.path.isdir(config_dir):
        return config_dir
    else:
        raise FileNotFoundError(f'ArmarX config folder does not exists. (Tried: "{config_dir}")')


def get_packages():
    """
    Lists all packages that are considered by the statecharts
    """
    default_packages = 'ArmarXGui,RobotAPI,VisionX,RobotSkillTemplates,ActiveVision'
    return config.get('AutoCompletion', 'packages', fallback=default_packages)


def get_ice_config_files():
    """
    The default Ice.Config
    """
    config_dir = os.path.expanduser(_get_config_dir())
    return [os.path.join(config_dir, 'default.generated.cfg'),
            os.path.join(config_dir, 'default.cfg')]


config = _load_config()
