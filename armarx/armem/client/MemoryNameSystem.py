import time
from typing import Dict, Any, List, Optional, Callable, Union

from armarx import slice_loader
from armarx.ice_manager import get_proxy

slice_loader.load_armarx_slice("RobotAPI", "armem/server/MemoryInterface.ice")
slice_loader.load_armarx_slice("RobotAPI", "armem/mns/MemoryNameSystemInterface.ice")
import armarx.armem as armem


from armarx.armem.core import MemoryID, error as armem_error
from armarx.armem.client.Reader import Reader
from armarx.armem.client.Writer import Writer



class MemoryNameSystem:

    Callback = Callable[[MemoryID, List[MemoryID]], None]
    UpdatedSnasphotIDs = List[Union[MemoryID, "armarx.armem.data.MemoryID"]]

    MemoryNameSystemPrx = "armarx.armem.mns.MemoryNameSystemInterfacePrx"
    MemoryServerPrx = "armarx.armem.server.MemoryInterfacePrx"



    def __init__(
            self,
            mns: Optional[MemoryNameSystemPrx]
            ):

        self.mns = mns
        self.servers: Dict[str, MemoryServer] = {}


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
            input.timeoutMilliSeconds = timeout_ms

            result = self.mns.waitForMemory(inputs)
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

    def get_all_readers(self, update=True) -> Dict[str, Reader]:
        return self._get_all_clients(Reader, update)

    def get_writer(self, memory_id: MemoryID) -> Writer:
        return Writer(self.resolve_server(memory_id))

    def get_all_writers(self, update=True) -> Dict[str, Writer]:
        return self._get_all_clients(Writer, update)


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
        import logging

        try:
            return get_proxy(armem.server.MemoryInterfacePrx, proxy_name)

        except Ice.NotRegisteredException as e:
            logging.error(e)
            return None



