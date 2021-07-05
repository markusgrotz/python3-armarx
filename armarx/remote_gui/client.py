"""
This module provides functionality for remote GUI clients.

Classes:
 - Tab: Base class for remote tabs.
 - Client: Remote GUI client.
"""

from armarx.remote_gui.ice_wrapper import TabProxy, get_remote_gui_proxy
from armarx.remote_gui.widgets import Widget

from typing import List
import abc


class Tab:
    """
    This is a base class for remote GUI tabs.

    A remote GUI tab is identified by an id string.
    The structure of the GUI is defined via a single root widget.
    The root widget is usually a container widget which contains many child widgets.

    The :meth:`create_widget_tree` method must be overridden in derived class to create the root widget and all its children.

    The :meth:`on_update` method is called by the Client after updates have been received from the GUI.
    """

    def __init__(self, id: str):
        self.id = id
        self.root_widget = None
        self.proxy: TabProxy = None

    @abc.abstractmethod
    def create_widget_tree(self) -> Widget:
        """
        Creates a widget tree and returns the root widget of the tree.

        This method MUST be overridden by a derived class.

        In a derived class, you will create your widgets here and nest them via container widgets.
        You can store the widgets, which you want to access later (usually value widgets), as member variables.
        Widgets which are only used for layout or to display constant values can be created as local variables
        and need not be stored.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def on_update(self):
        """
        Updates the internal state after an update has been received from the GUI.

        This method CAN be overridden by a derived class.

        In a derived class, you can update your internal state according to the new updates from the GUI.
        """
        pass

    def connect(self, proxy: 'RemoteGuiInterfacePrx'):
        """Connect this instance with a remote GUI tab."""
        self.root_widget = self.create_widget_tree()
        proxy.createTab(self.id, self.root_widget.desc)
        self.proxy = TabProxy(proxy, self.id)
        self.proxy.initialize_widget(self.root_widget)

    def remove(self):
        """Remove this remote GUI tab."""
        self.proxy.remove()

    def receive_updates(self):
        """Receive updates from the remote GUI."""
        self.proxy.receive_updates()

    def send_updates(self):
        """Send updates to the remote GUI."""
        self.proxy.send_updates()


class Client:
    """The client connects to the remote GUI and manages tabs."""

    def __init__(self, provider_name: str = "RemoteGuiProvider"):
        self.provider_name = provider_name
        self.proxy = get_remote_gui_proxy(provider_name)
        self.tabs: List[Tab] = []

    def add_tab(self, tab: Tab):
        """Add a tab and establish a connection to the remote GUI."""
        tab.connect(self.proxy)
        self.tabs.append(tab)

    def remove_tab(self, tab: Tab):
        """Remove a tab from the remote GUI."""
        tab.remove()
        self.tabs.remove(tab)

    def receive_updates(self):
        """Receive updates from the remote GUI for all added tabs."""
        for tab in self.tabs:
            tab.receive_updates()
            tab.on_update()

    def send_updates(self):
        """Send updates to the remote GUI for all added tabs."""
        for tab in self.tabs:
            tab.send_updates()
