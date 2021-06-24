from typing import Dict, Any, List, Optional, Callable, Union
import logging

import armarx
from armarx import slice_loader, ice_manager

slice_loader.load_armarx_slice("RobotAPI", "armem/server/MemoryInterface.ice")
slice_loader.load_armarx_slice("RobotAPI", "armem/mns/MemoryNameSystemInterface.ice")

from armarx import armem


from armarx.mem.core import MemoryID, error as armem_error
from armarx.mem.client.Reader import Reader
from armarx.mem.client.Writer import Writer


class MemoryNameSystem:

    cls_logger = logging.getLogger(__file__)

    Callback = Callable[[MemoryID, List[MemoryID]], None]
    UpdatedSnasphotIDs = List[Union[MemoryID, "armarx.armem.data.MemoryID"]]

    MemoryNameSystemPrx = "armarx.armem.mns.MemoryNameSystemInterfacePrx"
    MemoryServerPrx = "armarx.armem.server.MemoryInterfacePrx"


    @classmethod
    def get_mns(cls, mns_name="MemoryNameSystem", **kwargs) -> "MemoryNameSystem":
        import Ice

        try:
            mns_proxy = ice_manager.get_proxy(
                armarx.armem.mns.MemoryNameSystemInterfacePrx, mns_name)
            return MemoryNameSystem(mns_proxy, **kwargs)

        except Ice.NotRegisteredException as e:
            cls.cls_logger.error(e)
            raise armem_error.ArMemError(f"Memory Name System '{MemoryNameSystem}' is not registered.")

    @classmethod
    def wait_for_mns(cls, mns_name="MemoryNameSystem", **kwargs) -> "MemoryNameSystem":
        mns_proxy = ice_manager.wait_for_proxy(
            armem.mns.MemoryNameSystemInterfacePrx, mns_name, timeout=0)
        return MemoryNameSystem(mns_proxy, **kwargs)


    def __init__(
            self,
            mns: Optional[MemoryNameSystemPrx],
            logger=None,
            ):

        self.mns = mns
        self.servers: Dict[str, MemoryServer] = {}

        self.subscriptions: Dict[MemoryID, List[Callback]] = {}

        self.logger = logger or self.cls_logger


    # Server Resolution


    def update(self):

        result: "armem.data.GetAllRegisteredMemoriesResult"
        try:
            result = self.mns.getAllRegisteredMemories()
        except Ice.NotRegisteredException as e:
            raise ArMemError(e)
        if result.success:
            # Do some implicit type check
            self.servers = {name: server for name, server in result.proxies.items()}
        else:
            raise armem_error.ArMemError(f"MemoryNameSystem query failed: {result.errorMessage}")


    def resolve_server(
            self,
            memory_id: MemoryID,
            ) -> MemoryServerPrx:

        server = self.servers.get(memory_id.memory_name, None)

        if server is None:
            self.update()
            server = self.servers.get(memory_id.memory_name, None)
            if server is None:
                raise armem_error.CouldNotResolveMemoryServer(memory_id)

        assert server is not None
        return server

    def wait_for_server(
            self,
            memory_id: MemoryID,
            timeout_ms=-1,
            ) -> MemoryServerPrx:

        server = self.servers.get(memory_id.memory_name, None)
        if server is None:
            inputs = armem.data.WaitForMemoryInput()
            inputs.name = memory_id.memory_name
            inputs.timeoutMilliSeconds = timeout_ms

            self.logger.info(f"Waiting for memory server {memory_id} ...")
            result = self.mns.waitForMemory(inputs)
            self.logger.info(f"Resolved memory server {memory_id}.")
            if result.success:
                if result.proxy:
                    server = result.proxy
                else:
                    raise armem_error.CouldNotResolveMemoryServer(
                        memory_id, f"Returned proxy is null: {result.proxy}")
            else:
                raise armem_error.CouldNotResolveMemoryServer(memory_id, result.errorMessage)

        assert server is not None
        return server


    def get_reader(self, memory_id: MemoryID) -> Reader:
        return Reader(self.resolve_server(memory_id))

    def wait_for_reader(self, memory_id: MemoryID) -> Reader:
        return Reader(self.wait_for_server(memory_id))

    def get_all_readers(self, update=True) -> Dict[str, Reader]:
        return self._get_all_clients(Reader, update)

    def get_writer(self, memory_id: MemoryID) -> Writer:
        return Writer(self.resolve_server(memory_id))

    def wait_for_writer(self, memory_id: MemoryID) -> Writer:
        return Writer(self.wait_for_server(memory_id))

    def get_all_writers(self, update=True) -> Dict[str, Writer]:
        return self._get_all_clients(Writer, update)


    # ToDo: System-wide queries and commits


    def resolve_entity_instance(
            self,
            id: MemoryID,
            ) -> Optional["armem.data.EntityInstance"]:
        instances = self.resolve_entity_instances([id])
        if len(instances) > 0:
            return instances[entity_instance_id]
        else:
            return None


    def resolve_entity_instances(
            self,
            ids: List[MemoryID],
            ) -> Dict[MemoryID, "armem.data.EntityInstance"]:
        ids_per_memory = dict()
        for id in ids:
            if id.memory_name in ids_per_memory:
                ids_per_memory[id.memory_name].append(id)
            else:
                ids_per_memory[id.memory_name] = [id]

        result = dict()
        for memory_name, ids in ids_per_memory.items():
            reader = self.get_reader(memory_id=MemoryID(memory_name))
            try:
                snapshots = reader.query_snapshots(ids)
                result = {**result, **snapshots}
            except RuntimeError as e:
                pass
        return result


    # Subscription


    def subscribe(self, subscription_id: MemoryID, callback: Callback):
        """
        Subscribe a memory ID in order to receive updates to it.
        :param subscription_id: The subscribed ID.
        :param callback: The callback to be called with the updated IDs.
        """
        if subscription_id not in self.subscriptions:
            self.subscriptions[subscription_id] = [callback]
        else:
            self.subscriptions[subscription_id].append(callback)


    def updated(self, updated_snapshot_ids: UpdatedSnasphotIDs):
        """
        Function to be called when receiving messages over MemoryListener topic.
        :param updated_snapshot_ids: The updated snapshot IDs.
        """
        # Convert from Ice
        updated_snapshot_ids: List[MemoryID] = [
            id if isinstance(id, MemoryID) else MemoryID.from_ice(id)
            for id in updated_snapshot_ids
        ]
        for id in updated_snapshot_ids:
            assert isinstance(id, MemoryID)

        for subscribed_id, callbacks in self.subscriptions.items():
            # Split by subscribed id
            matching_snapshot_ids = [
                updated_snapshot_id for updated_snapshot_id in updated_snapshot_ids
                if subscribed_id.contains(updated_snapshot_id)
            ]
            # Call callbacks
            if len(matching_snapshot_ids) > 0:
                for callback in callbacks:
                    callback(subscribed_id, matching_snapshot_ids)


    def _get_all_clients(self, client_cls, update: bool):
        if update:
            self.update()
        return {name: client_cls(server) for name, server in self.servers}


    def __bool__(self):
        return bool(self.mns)


    @classmethod
    def get_server_by_proxy_name(
            cls, proxy_name: str,
            ) -> "armarx.armem.server.MemoryInterfacePrx":
        """
        Get a memory server proxy by its Ice object name.
        :param proxy_name: The ice object name.
        :return: The server proxy, if it exists.
        :throw: Ice.NotRegisteredException If the server does not exist.
        """
        import Ice

        try:
            return ice_manager.get_proxy(armem.server.MemoryInterfacePrx, proxy_name)

        except Ice.NotRegisteredException as e:
            cls.cls_logger.error(e)
            return None

