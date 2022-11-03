from typing import Dict, List, Optional
import logging

import armarx
from armarx_core import slice_loader
from armarx_core import ice_manager

slice_loader.load_armarx_slice("RobotAPI", "armem/server/MemoryInterface.ice")
slice_loader.load_armarx_slice("RobotAPI", "armem/mns/MemoryNameSystemInterface.ice")

from armarx import armem


from armarx_memory.core import MemoryID, error as armem_error
from armarx_memory.client.Reader import Reader
from armarx_memory.client.Writer import Writer


class ServerProxies:
    def __init__(
        self,
        reading: Optional[armem.server.ReadingMemoryInterface] = None,
        writing: Optional[armem.server.WritingMemoryInterface] = None,
    ):
        self.reading = reading
        self.writing = writing

    @classmethod
    def from_ice(cls, server: armem.mns.dto.MemoryServerInterfaces):
        return cls(reading=server.reading, writing=server.writing)


class MemoryNameSystem:

    cls_logger = logging.getLogger(__file__)

    MemoryNameSystemPrx = "armarx.armem.mns.MemoryNameSystemInterfacePrx"
    MemoryServerPrx = "armarx.armem.server.MemoryInterfacePrx"

    @classmethod
    def get_mns(cls, mns_name="MemoryNameSystem", **kwargs) -> "MemoryNameSystem":
        import Ice

        try:
            mns_proxy = ice_manager.get_proxy(
                armarx.armem.mns.MemoryNameSystemInterfacePrx, mns_name
            )
            return MemoryNameSystem(mns_proxy, **kwargs)

        except Ice.NotRegisteredException as e:
            cls.cls_logger.error(e)
            raise armem_error.ArMemError(
                f"Memory Name System '{MemoryNameSystem}' is not registered."
            )

    @classmethod
    def wait_for_mns(
        cls, mns_name="MemoryNameSystem", logger=None, **kwargs
    ) -> "MemoryNameSystem":
        if logger is not None:
            logger.info("Wait for Memory Name System ... ")

        mns_proxy = ice_manager.wait_for_proxy(
            armem.mns.MemoryNameSystemInterfacePrx, mns_name, timeout=0
        )

        if logger is not None:
            logger.info("Done.")

        return MemoryNameSystem(mns_proxy, **kwargs)

    def __init__(
        self,
        mns: Optional[MemoryNameSystemPrx],
        logger=None,
    ):

        self.mns = mns
        self.servers: Dict[str, ServerProxies] = {}

        self.logger = logger or self.cls_logger

    # Server Resolution

    def update(self):
        import Ice

        result: "armem.data.GetAllRegisteredMemoriesResult"
        try:
            result = self.mns.getAllRegisteredServers()
        except Ice.NotRegisteredException as e:
            raise armem_error.ArMemError(e)
        if result.success:
            # Do some implicit type check
            self.servers = {
                name: ServerProxies.from_ice(server)
                for name, server in result.servers.items()
            }
        else:
            raise armem_error.ArMemError(
                f"MemoryNameSystem query failed: {result.errorMessage}"
            )

    def resolve_server(
        self,
        memory_id: MemoryID,
    ) -> ServerProxies:

        server = self.servers.get(memory_id.memory_name, None)

        if server is None:
            self.update()
            server = self.servers.get(memory_id.memory_name, None)
            if server is None:
                raise armem_error.CouldNotResolveMemoryServer(memory_id)

        assert server is not None
        return server

    def wait_for_server(self, memory_id: MemoryID) -> ServerProxies:

        server = self.servers.get(memory_id.memory_name, None)
        if server is None:
            inputs = armem.mns.dto.WaitForServerInput(
                name=memory_id.memory_name,
            )

            self.logger.info(f"Waiting for memory server {memory_id} ...")
            result: armem.mns.dto.WaitForServerResult = self.mns.waitForServer(inputs)
            self.logger.info(f"Resolved memory server {memory_id}.")
            if result.success:
                if result.server.reading or result.server.writing:
                    server = ServerProxies.from_ice(result.server)
                else:
                    raise armem_error.CouldNotResolveMemoryServer(
                        memory_id, f"Returned proxy is null: {result.proxy}"
                    )
            else:
                raise armem_error.CouldNotResolveMemoryServer(
                    memory_id, result.errorMessage
                )

        assert server is not None
        return server

    def get_reader(self, memory_id: MemoryID) -> Reader:
        return Reader(self.resolve_server(memory_id).reading)

    def wait_for_reader(self, memory_id: MemoryID) -> Reader:
        return Reader(self.wait_for_server(memory_id).reading)

    def get_all_readers(self, update=True) -> Dict[str, Reader]:
        return self._get_all_clients(Reader, update)

    def get_writer(self, memory_id: MemoryID) -> Writer:
        return Writer(self.resolve_server(memory_id).writing)

    def wait_for_writer(self, memory_id: MemoryID) -> Writer:
        return Writer(self.wait_for_server(memory_id).writing)

    def get_all_writers(self, update=True) -> Dict[str, Writer]:
        return self._get_all_clients(Writer, update)

    # System-wide queries

    def resolve_entity_instance(
        self,
        id: MemoryID,
    ) -> Optional["armem.data.EntityInstance"]:
        instances = self.resolve_entity_instances([id])
        if len(instances) > 0:
            return instances[id]
        else:
            return None

    def resolve_entity_snapshots(
        self,
        ids: List[MemoryID],
    ) -> Dict[MemoryID, "armem.data.EntitySnapshot"]:
        errors = ""
        error_counter = 0

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
                result = {**result, **snapshots}  # Merge dicts
            except RuntimeError as e:
                error_counter += 1
                errors += f"\n#{error_counter}\n"
                errors += f"Failed to retrieve IDs {ids} from query result: \n{e}"

        if errors:
            self.logger.info(
                f"{self.__class__.__name__}.{self.resolve_entity_instance.__name__}:"
                f"The following errors may affect your result: \n{errors}\n\n"
                + "When resolving entity snapshots: \n- {}".format(
                    "\n- ".join(map(str, ids))
                )
            )

        return result

    # ToDo: System-wide commits

    def _get_all_clients(self, client_cls, update: bool):
        if update:
            self.update()
        return {name: client_cls(server) for name, server in self.servers}

    def __bool__(self):
        return bool(self.mns)

    @classmethod
    def get_server_by_proxy_name(
        cls,
        proxy_name: str,
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
