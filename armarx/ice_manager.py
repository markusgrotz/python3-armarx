import os
import time

import logging
from typing import Any
from typing import TypeVar

from functools import lru_cache

import Ice
from Ice import NotRegisteredException

from IceGrid import RegistryPrx
from IceGrid import ObjectExistsException

from IceStorm import TopicManagerPrx
from IceStorm import NoSuchTopic
from IceStorm import AlreadySubscribed

from .config import get_ice_config_files
from .name_helper import get_ice_default_name

logger = logging.getLogger(__name__)


T = TypeVar("T")


def register_object(
    ice_object: Ice.Object, ice_object_name: str = None
) -> Ice.ObjectPrx:
    """
    Register a local ice object under the given name

    :param ice_object: Local ice object instance
    :param ice_object_name: Name with which the object should be registered
    :return: Proxy to this object
    """
    if not isinstance(ice_object, Ice.Object):
        logger.error("ice object is not an Ice.Object")
        raise ValueError("ice_object is not an Ice.Object")
    if not ice_object_name:
        ice_object_name = ice_object.__class__.__name__
        logger.debug("Using class name %s to register the object", ice_object_name)
    adapter = freezer().communicator.createObjectAdapterWithEndpoints(
        ice_object_name, "tcp"
    )
    ice_object_id = freezer().communicator.stringToIdentity(ice_object_name)
    adapter.add(ice_object, ice_object_id)
    adapter.activate()
    proxy = adapter.createProxy(ice_object_id)
    admin = get_admin()
    try:
        logger.info("adding new object %s", ice_object_name)
        admin.addObjectWithType(proxy, proxy.ice_id())
    except ObjectExistsException:
        logger.info("updating new object %s", ice_object_name)
        admin.updateObject(proxy)
    return proxy


def get_topic(cls: T, topic_name: str = None) -> T:
    """
    Retrieve a topic proxy casted to the first parameter

    :param cls: Type of the topic
    :param topic_name: Name of the topic
    :type topic_name: str
    :return: a casted topic proxy
    """
    topic_name = topic_name or get_ice_default_name(cls)
    topic_manager = TopicManagerPrx.checkedCast(
        freezer().communicator.stringToProxy("IceStorm/TopicManager")
    )
    topic = None
    try:
        topic = topic_manager.retrieve(topic_name)
    except NoSuchTopic:
        topic = topic_manager.create(topic_name)
    logger.info("Publishing to topic %s", topic_name)
    pub = topic.getPublisher().ice_oneway()
    return cls.uncheckedCast(pub)


def using_topic(proxy, topic_name: str = None):
    """
    .. seealso:: :func:`register_object`

    :param proxy: the instance where the topic event should be called
    :param topic_name: the name of the topic to connect to
    :type topic_name: str
    """
    topic_manager = TopicManagerPrx.checkedCast(
        freezer().communicator.stringToProxy("IceStorm/TopicManager")
    )
    topic = None
    topic_name = topic_name or get_ice_default_name(proxy.__class__)
    try:
        topic = topic_manager.retrieve(topic_name)
    except NoSuchTopic:
        topic = topic_manager.create(topic_name)
    try:
        topic.subscribeAndGetPublisher(None, proxy)
    except AlreadySubscribed:
        topic.unsubscribe(proxy)
        topic.subscribeAndGetPublisher(None, proxy)
    logger.info("Subscribing to topic %s", topic_name)
    return topic


def wait_for_dependencies(proxy_names, timeout: int = 0):
    """
    waits for a dependency list

    :param proxy_names: the proxy names to wait for
    :type proxy_names: list of str

    :returns:  True if all dependencies are resolved
    :rtype: bool
    """
    start_time = time.time()
    while not freezer().communicator.isShutdown():
        if timeout and (start_time + timeout) < time.time():
            logging.exception("Timeout while waiting for proxies %s", proxy_names)
            return False
        dependencies_resolved = True
        for proxy_name in proxy_names:
            try:
                proxy = freezer().communicator.stringToProxy(proxy_name)
                proxy.ice_ping()
            except NotRegisteredException:
                dependencies_resolved = False
        if dependencies_resolved:
            return True
        else:
            time.sleep(0.1)


def wait_for_proxy(cls, proxy_name: str = None, timeout: int = 0):
    """
    waits for a proxy.

    :param cls: the class definition of an ArmarXComponent
    :param proxy_name: name of the proxy
    :param timeout: timeout in seconds to wait for the proxy. Zero means to wait forever
    :returns: the retrieved proxy
    :rtype: an instance of cls
    """
    proxy = None
    proxy_name = proxy_name or get_ice_default_name(cls)
    start_time = time.time()
    while not freezer().communicator.isShutdown() and proxy is None:
        try:
            proxy = freezer().communicator.stringToProxy(proxy_name)
            proxy_cast = cls.checkedCast(proxy)
            return proxy_cast
        except NotRegisteredException:
            proxy = None

        if timeout and (start_time + timeout) < time.time():
            logging.exception("Timeout while waiting for proxy %s", proxy_name)
            return None
        else:
            logger.debug("Waiting for proxy %s", proxy_name)
            time.sleep(0.1)


def get_proxy(cls: T, proxy_name: str = None) -> T:
    """
    Connects to a proxy.

    :param cls: the class definition of an ArmarXComponent
    :param proxy_name: name of the proxy
    :type proxy_name: str
    :returns: the retrieved proxy
    :rtype: an instance of cls
    :raises: Ice::NotRegisteredException if the proxy is not available
    """
    proxy_name = proxy_name or get_ice_default_name(cls)
    try:
        proxy = freezer().communicator.stringToProxy(proxy_name)
        return cls.checkedCast(proxy)
    except NotRegisteredException:
        logging.exception("Proxy %s does not exist", proxy_name)


def get_admin():
    return freezer().registry.createAdminSession("user", "password").getAdmin()


def is_connected(ice_node_name: str) -> bool:
    return get_admin().pingNode(ice_node_name)


def is_alive() -> bool:
    """
    checks if shutdown has been invoked on the communicator.

    :returns: true if ice grid registry is alive
    """
    return not freezer().communicator.isShutdown()


def wait_for_shutdown():
    """
    sleeps until the ice communicator receives a shutdown signal
    or the program receives a keyboard interrupt
    """
    try:
        freezer().communicator.waitForShutdown()
    except KeyboardInterrupt:
        pass


@lru_cache(maxsize=1)
def freezer():
    """ """
    return Freezer()


def test_connection():
    if not is_connected("NodeMain"):
        logger.error("Ice is not running.")
        raise Exception("Ice is not running.")


class Freezer:

    registry: RegistryPrx = None
    communicator = None

    def __init__(self):
        ice_config_files = get_ice_config_files()
        ice_communicator = Ice.initialize(
            ["--Ice.Config={}".format(",".join(ice_config_files))]
        )
        ice_registry_proxy = ice_communicator.stringToProxy("IceGrid/Registry")
        ice_registry = RegistryPrx.checkedCast(ice_registry_proxy)

        self.communicator = ice_communicator
        self.registry = ice_registry
        import atexit

        atexit.register(self.__del__)

    @property
    def admin(self):
        return self.registry.createAdminSession("user", "password").getAdmin()

    def __enter__(self):
        return self.communicator

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def shutdown(self):
        if not self.communicator:
            return
        try:
            self.communicator.destroy()
        except Exception as ex:
            logger.error("Error while shutting down ice communicator")
        finally:
            self.communicator = None

    def __del__(self):
        self.shutdown()
