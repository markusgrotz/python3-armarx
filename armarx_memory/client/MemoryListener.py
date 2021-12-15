from typing import Dict, Any, List, Optional, Callable, Union
import logging

from armarx import slice_loader, ice_manager
slice_loader.load_armarx_slice("RobotAPI", "armem/client/MemoryListenerInterface.ice")

from armarx import armem

from armarx.mem.core.MemoryID import MemoryID
from armarx.mem.client.MemoryNameSystem import MemoryNameSystem


logger = logging.getLogger(__file__)


class MemoryListener(armem.client.MemoryListenerInterface):

    def __init__(self,
                 name: Optional[str] = None,
                 topic_name: str = "MemoryUpdates",
                 mns_clients: Optional[Union[MemoryNameSystem, List[MemoryNameSystem]]] = None,
                 ):
        self.name = name
        self.topic_name = topic_name

        # MNS clients that shall receive memory updates to handle subscriptions.
        if mns_clients is None:
            self.mns_clients = []
        elif isinstance(mns_clients, MemoryNameSystem):
            self.mns_clients = [mns_clients]
        else:
            self.mns_clients = mns_clients


    def register(self, log_fn=None):
        if log_fn is not None:
            log_fn(f"Register {self.__class__.__name__} '{self.name}' "
                   f"listening to topic '{self.topic_name}' ...")

        proxy = ice_manager.register_object(self, self.name)
        ice_manager.using_topic(proxy, self.topic_name)
        return proxy


    def memoryUpdated(self, updated_snapshot_ids: List[armem.data.MemoryID], c=None):
        """Called by the MemoryListenerTopic."""
        updated_snapshot_ids = MemoryID.from_ice(updated_snapshot_ids)
        for mns in self.mns_clients:
            mns.updated(updated_snapshot_ids=updated_snapshot_ids)
