import typing as ty
import logging

from armarx_core import slice_loader
from armarx_core import ice_manager

slice_loader.load_armarx_slice("RobotAPI", "armem/client/MemoryListenerInterface.ice")

from armarx import armem

from armarx_memory.core.MemoryID import MemoryID


logger = logging.getLogger(__file__)


class MemoryListener(armem.client.MemoryListenerInterface):

    Callback = ty.Callable[[MemoryID, ty.List[MemoryID]], None]
    UpdatedSnapshotIDs = ty.List[ty.Union[MemoryID, "armarx.armem.data.MemoryID"]]

    TopicNameFormat = "MemoryUpdates.{memory_name}"

    def __init__(
        self,
        name: ty.Optional[str] = None,
        register=True,
        log_fn=None,
    ):
        self.name = name
        self.proxy = None

        if log_fn is None:

            def log_fn(*args, **kwargs):
                pass

        self.log_fn = log_fn

        self.subscriptions: ty.Dict[MemoryID, ty.List["MemoryListener.Callback"]] = {}

        if register:
            self.register()

    def register(self):
        self.log_fn(f"Register {self.__class__.__name__} '{self.name}' ...")

        self.proxy = ice_manager.register_object(self, self.name)
        return self.proxy

    def use_topic_of_id(self, memory_id: MemoryID):
        topic_name = self.TopicNameFormat.format(memory_name=memory_id.memory_name)
        self.log_fn(f"'{self.name}': Use topic '{topic_name}'.")
        ice_manager.using_topic(self.proxy, topic_name)

    def subscribe(self, subscription_id: MemoryID, callback: Callback):
        """
        Subscribe a memory ID in order to receive updates to it.
        :param subscription_id: The subscribed ID.
        :param callback: The callback to be called with the updated IDs.
        """
        self.log_fn(f"'{self.name}': Subscribe to {subscription_id}.")
        self.use_topic_of_id(memory_id=subscription_id)
        if subscription_id not in self.subscriptions:
            self.subscriptions[subscription_id] = [callback]
        else:
            self.subscriptions[subscription_id].append(callback)

    def updated(self, updated_snapshot_ids: UpdatedSnapshotIDs):
        """
        Function to be called when receiving messages over MemoryListener topic.
        :param updated_snapshot_ids: The updated snapshot IDs.
        """
        # Convert from Ice
        updated_snapshot_ids: ty.List[MemoryID] = [
            id if isinstance(id, MemoryID) else MemoryID.from_ice(id)
            for id in updated_snapshot_ids
        ]
        for id in updated_snapshot_ids:
            assert isinstance(id, MemoryID)

        for subscribed_id, callbacks in self.subscriptions.items():
            # Split by subscribed id
            matching_snapshot_ids = [
                updated_snapshot_id
                for updated_snapshot_id in updated_snapshot_ids
                if subscribed_id.contains(updated_snapshot_id)
            ]
            # Call callbacks
            if len(matching_snapshot_ids) > 0:
                for callback in callbacks:
                    callback(subscribed_id, matching_snapshot_ids)

    def memoryUpdated(self, updated_snapshot_ids: ty.List[armem.data.MemoryID], c=None):
        """Called via the MemoryListenerTopic."""
        updated_snapshot_ids = MemoryID.from_ice(updated_snapshot_ids)
        self.updated(updated_snapshot_ids)
