from typing import Dict, Any, List, Optional, Callable, Union

from armarx import slice_loader
slice_loader.load_armarx_slice("RobotAPI", "armem/query.ice")

from armarx import armem

from armarx_memory.core import MemoryID


class Reader:

    ReadingMemoryServerPrx = "armem.server.ReadingMemoryInterfacePrx"
    qd = armem.query.data


    def __init__(
            self,
            server: Optional[ReadingMemoryServerPrx],
            ):

        self.server = server


    def query(
            self,
            queries: List[armem.query.data.MemoryQuery],
            ) -> armem.data.Memory:
        """
        Perform a memory query. Return the result if successful,
        otherwise raise an exception.
        :param queries: The query(s)
        :return: The result, if successful.
        """

        inp = self.qd.Input(memoryQueries=queries, withData=True)
        result = self.server.query(inp)
        if not result.success:
            raise RuntimeError(f"Memory query failed. Reason:\n{result.errorMessage}")
        else:
            return result.memory


    def query_snapshots(
            self,
            ids: List[MemoryID],
            ) -> Dict[MemoryID, armem.data.EntitySnapshot]:
        """
        Query snapshots corresponding to list of memory IDs.

        Each ID can refer to an entity, a snapshot or an instance. When not
        referring to an entity snapshot, the latest snapshot will be queried.

        All memory IDs must refer to the memory this reader is reading from.
        If an ID refers to another memory, the query will not find it and it
        will not be part of the result.

        :param ids: The entity, snapshot or instance IDs.
        :return: The query result, if successful.
        """

        qs_memory = []
        for snapshot_id in ids:
            if snapshot_id.timestamp_usec >= 0:
                q_entity = self.qd.entity.Single(timestamp=snapshot_id.timestamp_usec)
            else:
                q_entity = self.qd.entity.Single()  # Latest

            q_prov = self.qd.provider.Single(entityName=snapshot_id.entity_name,
                                             entityQueries=[q_entity])
            q_core = self.qd.core.Single(providerSegmentName=snapshot_id.provider_segment_name,
                                         providerSegmentQueries=[q_prov])
            q_memory = self.qd.memory.Single(coreSegmentName=snapshot_id.core_segment_name,
                                             coreSegmentQueries=[q_core])
            qs_memory.append(q_memory)

        memory = self.query(qs_memory)

        snapshots = dict()
        for id in ids:
            entity = (memory.coreSegments[id.core_segment_name]
                .providerSegments[id.provider_segment_name]
                .entities[id.entity_name])
            snapshots[id] = entity.history[
                id.timestamp_usec
                if id.timestamp_usec >= 0
                else max(entity.history.keys())
            ]
        return snapshots


    def query_snapshot(
            self,
            snapshot_id: MemoryID,
            ) -> armem.data.EntitySnapshot:

        return self.query_snapshots([snapshot_id])[snapshot_id]


    def query_all(
            self,
            ) -> armem.data.Memory:

        q_entity = self.qd.entity.All()
        q_prov = self.qd.provider.All(entityQueries=[q_entity])
        q_core = self.qd.core.All(providerSegmentQueries=[q_prov])
        q_memory = self.qd.memory.All(coreSegmentQueries=[q_core])
        memory = self.query([q_memory])
        return memory


    def query_core_segment(
            self,
            name: str,
            regex=False,
            latest_snapshot=False,
            ) -> armem.data.Memory:

        if latest_snapshot:
            q_entity = self.qd.entity.Single()  # Latest
        else:
            q_entity = self.qd.entity.All()
        q_prov = self.qd.provider.All(entityQueries=[q_entity])
        q_core = self.qd.core.All(providerSegmentQueries=[q_prov])
        if regex:
            q_memory = self.qd.memory.Regex(coreSegmentNameRegex=name,
                                            coreSegmentQueries=[q_core])
        else:
            q_memory = self.qd.memory.Single(coreSegmentName=name,
                                             coreSegmentQueries=[q_core])
        memory = self.query([q_memory])
        return memory


    def query_latest(
            self,
            memory_id: Optional[MemoryID] = None,
            ) -> armem.data.Memory:
        if memory_id is None:
            memory_id = MemoryID()

        q_entity = self.qd.entity.Single()  # Latest
        if memory_id.entity_name:
            q_prov = self.qd.provider.Single(entityName=memory_id.entity_name,
                                             entityQueries=[q_entity])
        else:
            q_prov = self.qd.provider.All(entityQueries=[q_entity])

        if memory_id.provider_segment_name:
            q_core = self.qd.core.Single(providerSegmentName=memory_id.provider_segment_name,
                                         providerSegmentQueries=[q_prov])
        else:
            q_core = self.qd.core.All(providerSegmentQueries=[q_prov])


        if memory_id.core_segment_name:
            q_memory = self.qd.memory.Single(coreSegmentName=memory_id.core_segment_name,
                                             coreSegmentQueries=[q_core])
        else:
            q_memory = self.qd.memory.All(coreSegmentQueries=[q_core])


        memory = self.query([q_memory])
        return memory



    def __bool__(self):
        return bool(self.server)
