import logging

import time
import os
import configparser


import Ice
from IceGrid import ObjectExistsException, RegistryPrx
from IceStorm import TopicManagerPrx, NoSuchTopic, AlreadySubscribed
from Ice import NotRegisteredException


logger = logging.getLogger(__name__)


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
    :type topic_name: str
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


def wait_for_dependencies(proxy_names, timeout=0):
    """
    waits for a dependency list

    :param proxy_names: the proxy names to wait for
    :type proxy_names: list of str

    :returns:  True if all dependencies are resolved
    :rtype: bool
    """
    start_time = time.time()
    while not ice_communicator.isShutdown():
        if timeout and (start_time + timeout) < time.time():
            logging.exception('Timeout while waiting for proxy {}'.format(proxy_name))
            return False
        dependencies_resolved = True
        for proxy_name in proxy_names:
            try:
                proxy = ice_communicator.stringToProxy(proxy_name)
                proxy.ice_ping()
            except NotRegisteredException:
                dependencies_resolved = False
        if dependencies_resolved:
            return True
        else:
            time.sleep(0.1)


def wait_for_proxy(cls, proxy_name, timeout=0):
    """
    waits for a proxy.

    :param cls: the class definition of an ArmarXComponent
    :param proxy_name: name of the proxy
    :type proxy_name: str
    :param timeout: timeout in seconds to wait for the proxy. Zero means to wait forever
    :type timeout: int
    :returns: the retrieved proxy
    :rtype: an instance of cls
    """
    proxy = None
    start_time = time.time()
    while not ice_communicator.isShutdown() and proxy is None:
        try:
            proxy = ice_communicator.stringToProxy(proxy_name)
            proxy_cast = cls.checkedCast(proxy)
            return proxy_cast
        except NotRegisteredException:
            proxy = None
        if timeout and (start_time + timeout) < time.time():
            logging.exception('Timeout while waiting for proxy {}'.format(proxy_name))
            return
        else:
            logger.debug('Waiting for proxy {}'.format(proxy_name))
            time.sleep(0.1)


def get_proxy(cls, proxy_name):
    """
    Connects to a proxy.

    :param cls: the class definition of an ArmarXComponent
    :param proxy_name: name of the proxy
    :type proxy_name: str
    :returns: the retrieved proxy
    :rtype: an instance of cls
    :raises: Ice::NotRegisteredException if the proxy is not available
    """
    try:
        proxy = ice_communicator.stringToProxy(proxy_name)
        return cls.checkedCast(proxy)
    except NotRegisteredException:
        logging.exception('Proxy {} does not exist'.format(proxy_name))


def get_config_dir():
    """
    :raises IOError: if the $HOME/.armarx does not exists
    :returns: the default armarx config folder
    :rtype: str
    """
    config_dir = os.path.expanduser('~/.armarx/')
    if not os.path.isdir(config_dir):
        raise IOError('ArmarX config folder does not exists.')
    return config_dir


def load_config():
    """
    :raises IOError: if armarx.ini does not exists
    :returns: the default armarx config
    :rtype: configparser.ConfigParser
    """
    config_dir = get_config_dir()
    config_file = os.path.join(config_dir, 'armarx.ini')
    if not os.path.exists(config_file):
        raise IOError('ArmarX config file does not exists.')
    config = configparser.Configparser()
    config.read(config_file)
    return config


def get_admin():
    return ice_registry.createAdminSession('user', 'password').getAdmin()


def is_connected(ice_node_name):
    return get_admin().pingNode(ice_node_name)


def is_alive():
    """
    checks if shutdown has been invoked on the communicator. 

    :returns: true if ice grid registry is alive
    """
    return not ice_communicator.isShutdown()


def wait_for_shutdown():
    """
    sleeps until the ice communicator receives a shutdown signal 
    or the program receives a keyboard interrupt
    """
    try:
        ice_communicator.waitForShutdown()
    except KeyboardInterrupt:
        pass


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
