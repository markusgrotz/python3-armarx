import logging
import os
import configparser

import Ice
from IceGrid import ObjectExistsException, RegistryPrx
from IceStorm import TopicManagerPrx, NoSuchTopic, AlreadySubscribed

from .cmake_helper import get_dependencies, get_include_path

logger = logging.getLogger(__name__)


def load_armarx_slice(project, filename):
    """
    simple helper function to load a slice definition file.  The imported slice
    is then available through the python import function.

    :param project: name of the amrarx package
    :type project: str
    :param filename: relative path to the slice interface
    :type filename: str
    """
    dependencies = get_dependencies(project)
    dependencies.append(project)

    include_path = ['-I{}'.format(Ice.getSliceDir())]

    for package_name in dependencies:
        interface_dir = get_include_path(package_name)
        include_path.extend(interface_dir)

    filename = os.path.join(include_path[-1], project, 'interface', filename)

    search_path = ' -I'.join(include_path)
    logger.debug('Looking for slice files in {}'.format(search_path))
    if not os.path.exists(filename):
        raise IOError("Path not found: " + filename)
    Ice.loadSlice('{} --underscore --all {}'.format(search_path, filename))


def register_object(ice_object, ice_object_name):
    """
    Register an local ice object with ice under the given name
    :param ice_object: Local ice object instance
    :param ice_object_name: Name with which the object should be registered
    :return: Proxy to this object
    """
    adapter = ice_communicator.createObjectAdapterWithEndpoints(ice_object_name, 'tcp')
    ice_object_id = ice_communicator.stringToIdentity(ice_object_name)
    adapter.add(ice_object, ice_object_id)
    adapter.activate()
    proxy = adapter.createProxy(ice_object_id)
    admin = get_admin()
    try:
        logger.info('adding new object {}'.format(ice_object_name))
        admin.addObjectWithType(proxy, proxy.ice_id())
    except ObjectExistsException:
        logger.info('updating new object {}'.format(ice_object_name))
        admin.updateObject(proxy)
    return proxy


def get_topic(cls, topic_name):
    """
    Retrieve a topic proxy casted to the first parameter
    :param cls: Type of the topic
    :param topic_name: Name of the topic
    :return: a casted topic proxy
    """
    topic_manager = TopicManagerPrx.checkedCast(ice_communicator.stringToProxy('IceStorm/TopicManager'))
    topic = None
    try:
        topic = topic_manager.retrieve(topic_name)
    except NoSuchTopic:
        topic = topic_manager.create(topic_name)
    logger.info("Publishing to topic " + topic_name)
    pub = topic.getPublisher().ice_oneway()
    return cls.uncheckedCast(pub)


def using_topic(proxy, topic_name):
    """
    .. seealso:: :func:`register_object`

    :param proxy: the instance where the topic event should be called
    :param topic_name: the name of the topic to connect to
    :type topic_name: str
    """
    topic_manager = TopicManagerPrx.checkedCast(ice_communicator.stringToProxy('IceStorm/TopicManager'))
    topic = None
    try:
        topic = topic_manager.retrieve(topic_name)
    except NoSuchTopic:
        topic = topic_manager.create(topic_name)
    try:
        topic.subscribeAndGetPublisher(None, proxy)
    except AlreadySubscribed:
        topic.unsubscribe(proxy)
        topic.subscribeAndGetPublisher(None, proxy)
    logger.info("Subscribing to topic " + topic_name)
    return topic


def get_proxy(cls, proxy_name):
    """
    Connects to a proxy.

    :param cls: the class definition of an ArmarXComponent
    :param proxy_name: name of the proxy
    :type proxy_name: str
    :returns: the retrieved proxy
    :rtype: an instance of cls
    """
    proxy = ice_communicator.stringToProxy(proxy_name)
    return cls.checkedCast(proxy)


def get_config_dir():
    config_dir = os.path.expanduser('~/.armarx/')
    if not os.path.isdir(config_dir):
        raise Exception('ArmarX config folder does not exists.')
    return config_dir


def load_config():
    config_dir = get_config_dir()
    config_file = os.path.join(config_dir, 'armarx.ini')
    if not os.path.exists(config_file):
        raise Exception('ArmarX config file does not exists.')
    config = configparser.Configparser()
    config.read(config_file)

    return config


def get_admin():
    return ice_registry.createAdminSession('user', 'password').getAdmin()


def is_connected(ice_node_name):
    return get_admin().pingNode(ice_node_name)


def _initialize():
    config_path = get_config_dir()
    ice_config_files = [os.path.join(config_path, 'default.generated.cfg'),
                        os.path.join(config_path, 'default.cfg')]

    ice_communicator = Ice.initialize(['--Ice.Config={}'.format(','.join(ice_config_files))])
    ice_registry_proxy = ice_communicator.stringToProxy('IceGrid/Registry')
    ice_registry = RegistryPrx.checkedCast(ice_registry_proxy)
    return ice_communicator, ice_registry


def test_connection():
    if not is_connected('NodeMain'):
        logger.error('Ice is not running.')
        raise Exception('Ice is not running.')


ice_communicator, ice_registry = _initialize()

test_connection()
